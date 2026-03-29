#!/usr/bin/env python3
"""
Neo4j Weekly Cleanup Script for SecondBrain Graph
==================================================
Run weekly (or manually) to:
1. Remove Person nodes with null names
2. Remove Person nodes that look like concepts/phrases (not names)
3. Auto-merge duplicate Person nodes (same name, different case)
4. Ensure proper indexes exist on Person.name and SocialProfile.platform
5. Report before/after metrics

Usage:
    python3 neo4j_weekly_cleanup.py           # Full cleanup
    python3 neo4j_weekly_cleanup.py --dry-run # Report only, no changes
    python3 neo4j_weekly_cleanup.py --indexes-only # Just create indexes

Neo4j: bolt://localhost:7687
"""

import sys
import re
import json
import time
from datetime import datetime

try:
    from neo4j import GraphDatabase
except ImportError:
    print("ERROR: neo4j driver not installed. Run: pip3 install neo4j")
    sys.exit(1)

NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASS = "secondbrain2026"

DRY_RUN = "--dry-run" in sys.argv
INDEXES_ONLY = "--indexes-only" in sys.argv

# Name validation: a real person name should have these properties
# - At least 2 characters
# - Starts with uppercase letter
# - Contains only letters, spaces, hyphens, apostrophes, periods
# - No more than 4 words (most names are 2-3 words)
VALID_NAME_RE = re.compile(
    r"^[A-ZÀ-Ö][a-zA-ZÀ-öø-ÿ'\-\.]+(?:\s[A-ZÀ-Öa-zA-Zà-öø-ÿ'\-\.]+){0,3}$"
)

# Concept/phrase patterns that are NOT person names
CONCEPT_PATTERNS = [
    # Multi-word phrases that look like titles/concepts
    r"^(The|A|An)\s+",          # starts with article
    r"\s+(System|Process|Policy|Strategy|Platform|Framework|Service|Protocol|Program|Initiative|Project|Plan|Guide|Manual|Report|Review|Analysis|Assessment|Model|Method|Approach|Solution|Tool|Application)$",  # ends with concept word
    # Technical junk
    r"^[A-Z]{2,}\s",             # starts with acronym
    r"[A-Z]{3,}$",               # ends with acronym 3+ chars
    # Common false positives from LLM exports
    r"^(Content|Data|Default|Fire|Key|New|Old|Task|Issue|Type|Status|Current|Future|Recent|Main|Primary|Secondary|Basic|Advanced|General|Special|Standard|Custom)\s",
]

CONCEPT_COMPILED = [re.compile(p) for p in CONCEPT_PATTERNS]


def looks_like_name(name):
    """Return True if the name looks like a real person name."""
    if not name:
        return False
    if len(name) < 3:
        return False
    if not VALID_NAME_RE.match(name):
        return False
    for pattern in CONCEPT_COMPILED:
        if pattern.search(name):
            return False
    return True


def get_metrics(session):
    """Collect current graph metrics."""
    metrics = {}
    
    r = session.run("MATCH (p:Person) RETURN count(p) as cnt").single()
    metrics["person_total"] = r["cnt"]
    
    r = session.run("MATCH (p:Person) WHERE p.name IS NULL RETURN count(p) as cnt").single()
    metrics["person_null_name"] = r["cnt"]
    
    r = session.run("MATCH (p:Person) WHERE p.name IS NOT NULL RETURN count(p) as cnt").single()
    metrics["person_named"] = r["cnt"]
    
    r = session.run("MATCH (sp:SocialProfile) RETURN count(sp) as cnt").single()
    metrics["social_profiles"] = r["cnt"]
    
    r = session.run("MATCH ()-[r]->() RETURN count(r) as cnt").single()
    metrics["relationships"] = r["cnt"]
    
    r = session.run("MATCH (p:Person) WHERE NOT (p)--() RETURN count(p) as cnt").single()
    metrics["orphan_persons"] = r["cnt"]
    
    return metrics


def step_ensure_indexes(session):
    """Create indexes if they don't exist."""
    print("\n── Step: Ensure Indexes ──", flush=True)
    
    indexes_to_create = [
        ("SocialProfile", "platform", "CREATE INDEX social_profile_platform IF NOT EXISTS FOR (sp:SocialProfile) ON (sp.platform)"),
        ("SocialProfile", "username", "CREATE INDEX social_profile_username IF NOT EXISTS FOR (sp:SocialProfile) ON (sp.username)"),
        ("Person", "phone", "CREATE INDEX person_phone IF NOT EXISTS FOR (p:Person) ON (p.phone)"),
        ("Person", "email", "CREATE INDEX person_email IF NOT EXISTS FOR (p:Person) ON (p.email)"),
    ]
    
    created = 0
    for label, prop, query in indexes_to_create:
        if not DRY_RUN:
            session.run(query)
            print(f"  ✓ Index ensured: ({label}).{prop}", flush=True)
            created += 1
        else:
            print(f"  DRY-RUN: Would create index on ({label}).{prop}", flush=True)
    
    # List all current indexes
    result = session.run("SHOW INDEXES YIELD labelsOrTypes, properties, state WHERE state = 'ONLINE'")
    indexes = [(r["labelsOrTypes"], r["properties"]) for r in result]
    print(f"  Active indexes: {len(indexes)}", flush=True)
    
    return created


def step_remove_null_name_persons(session):
    """Remove Person nodes with null names (phone-only contacts with no name)."""
    print("\n── Step: Remove Null-Name Person Nodes ──", flush=True)
    
    r = session.run("MATCH (p:Person) WHERE p.name IS NULL RETURN count(p) as cnt").single()
    count = r["cnt"]
    print(f"  Found {count} Person nodes with null name", flush=True)
    
    if count == 0:
        return 0
    
    if DRY_RUN:
        print(f"  DRY-RUN: Would delete {count} null-name Person nodes", flush=True)
        return 0
    
    # Delete in batches to avoid memory issues
    deleted = 0
    batch_size = 500
    while True:
        r = session.run(f"""
            MATCH (p:Person) WHERE p.name IS NULL
            WITH p LIMIT {batch_size}
            DETACH DELETE p
            RETURN count(p) as cnt
        """).single()
        batch_deleted = r["cnt"]
        deleted += batch_deleted
        print(f"  Deleted batch: {batch_deleted} (total so far: {deleted})", flush=True)
        if batch_deleted < batch_size:
            break
    
    print(f"  ✓ Removed {deleted} null-name Person nodes", flush=True)
    return deleted


def step_remove_concept_persons(session):
    """Remove Person nodes that look like concepts/phrases rather than real names."""
    print("\n── Step: Remove Concept-as-Person Nodes ──", flush=True)
    
    # Get all named Person nodes (use elementId for neo4j 5.x compatibility)
    result = session.run("MATCH (p:Person) WHERE p.name IS NOT NULL RETURN elementId(p) as eid, p.name as name")
    
    to_delete = []
    for r in result:
        name = r["name"]
        if not looks_like_name(name):
            to_delete.append((r["eid"], name))
    
    print(f"  Found {len(to_delete)} nodes that look like concepts (not names)", flush=True)
    
    if DRY_RUN:
        print("  DRY-RUN: Would delete:", flush=True)
        for _, name in to_delete[:30]:
            print(f"    - {repr(name)}", flush=True)
        if len(to_delete) > 30:
            print(f"    ... and {len(to_delete)-30} more", flush=True)
        return 0
    
    if len(to_delete) > 0:
        print("  Sample of nodes to delete:", flush=True)
        for _, name in to_delete[:10]:
            print(f"    - {repr(name)}", flush=True)
        
        # Delete in batches (use elementId for neo4j 5.x compatibility)
        node_eids = [eid for eid, _ in to_delete]
        deleted = 0
        batch_size = 200
        for i in range(0, len(node_eids), batch_size):
            batch = node_eids[i:i+batch_size]
            r = session.run(
                "MATCH (p:Person) WHERE elementId(p) IN $eids DETACH DELETE p RETURN count(p) as cnt",
                eids=batch
            ).single()
            deleted += r["cnt"]
        
        print(f"  ✓ Removed {deleted} concept-as-Person nodes", flush=True)
        return deleted
    
    return 0


def step_merge_duplicate_persons(session):
    """Merge duplicate Person nodes with same name (case-insensitive)."""
    print("\n── Step: Merge Duplicate Person Nodes ──", flush=True)
    
    # Find groups with same lowercase name
    result = session.run("""
        MATCH (p:Person)
        WHERE p.name IS NOT NULL
        WITH toLower(p.name) as lower_name, collect(p) as nodes, count(p) as cnt
        WHERE cnt > 1
        RETURN lower_name, nodes, cnt
        ORDER BY cnt DESC
        LIMIT 100
    """)
    
    duplicates = [(r["lower_name"], r["nodes"], r["cnt"]) for r in result]
    print(f"  Found {len(duplicates)} groups with duplicate names", flush=True)
    
    if not duplicates:
        return 0
    
    if DRY_RUN:
        print("  DRY-RUN: Would merge:", flush=True)
        for lower_name, nodes, cnt in duplicates[:10]:
            names = [n["name"] for n in nodes]
            print(f"    {repr(lower_name)}: {names}", flush=True)
        return 0
    
    merged_count = 0
    for lower_name, nodes, cnt in duplicates:
        # Pick canonical node (prefer the one with the most properties)
        canonical = max(nodes, key=lambda n: len(dict(n)))
        others = [n for n in nodes if n.id != canonical.id]
        
        print(f"  Merging: {lower_name} ({cnt} nodes → 1)", flush=True)
        
        for other in others:
            other_id = other.id
            canonical_id = canonical.id
            
            # Transfer all relationships from other to canonical
            session.run("""
                MATCH (other:Person) WHERE id(other) = $other_id
                MATCH (canonical:Person) WHERE id(canonical) = $canonical_id
                
                // Redirect all incoming rels
                CALL {
                    WITH other, canonical
                    MATCH (x)-[r]->(other)
                    WHERE id(x) <> id(canonical)
                    WITH x, r, canonical, type(r) as rel_type, properties(r) as rel_props
                    CALL apoc.create.relationship(x, rel_type, rel_props, canonical) YIELD rel
                    DELETE r
                    RETURN count(*) as cnt
                }
                
                // Redirect all outgoing rels
                CALL {
                    WITH other, canonical
                    MATCH (other)-[r]->(x)
                    WHERE id(x) <> id(canonical)
                    WITH x, r, canonical, type(r) as rel_type, properties(r) as rel_props
                    CALL apoc.create.relationship(canonical, rel_type, rel_props, x) YIELD rel
                    DELETE r
                    RETURN count(*) as cnt
                }
                
                DETACH DELETE other
            """, other_id=other_id, canonical_id=canonical_id)
            merged_count += 1
    
    print(f"  ✓ Merged {merged_count} duplicate nodes", flush=True)
    return merged_count


def step_merge_duplicates_simple(session):
    """Simpler merge: just delete the duplicate, transferring no rels (for low-rel-count dupes)."""
    print("\n── Step: Merge Duplicate Person Nodes (simple) ──", flush=True)
    
    result = session.run("""
        MATCH (p:Person)
        WHERE p.name IS NOT NULL
        WITH toLower(p.name) as lower_name, collect(p) as nodes, count(p) as cnt
        WHERE cnt > 1
        RETURN lower_name, nodes, cnt
        ORDER BY cnt DESC
    """)
    
    duplicates = [(r["lower_name"], r["nodes"], r["cnt"]) for r in result]
    print(f"  Found {len(duplicates)} groups with duplicate names", flush=True)
    
    if not duplicates:
        return 0
    
    if DRY_RUN:
        print("  DRY-RUN: Would merge:", flush=True)
        for lower_name, nodes, cnt in duplicates[:10]:
            names = [n["name"] for n in nodes]
            print(f"    {repr(lower_name)}: {names}", flush=True)
        return 0
    
    merged_count = 0
    for lower_name, nodes, cnt in duplicates:
        # Keep the node with the most properties / relationships
        canonical_eid = canonical_score = None
        
        for node in nodes:
            node_eid = node.element_id
            # Get rel count
            r = session.run("MATCH (p) WHERE elementId(p) = $eid RETURN size((p)--()) as rels", eid=node_eid).single()
            prop_count = len(dict(node))
            rel_count = r["rels"] if r else 0
            score = prop_count + rel_count * 2
            if canonical_score is None or score > canonical_score:
                canonical_eid = node_eid
                canonical_score = score
        
        # Delete all others
        for node in nodes:
            if node.element_id != canonical_eid:
                session.run("MATCH (p) WHERE elementId(p) = $eid DETACH DELETE p", eid=node.element_id)
                merged_count += 1
    
    print(f"  ✓ Removed {merged_count} duplicate nodes (kept canonical)", flush=True)
    return merged_count


def step_remove_orphan_persons(session):
    """Remove Person nodes with no relationships."""
    print("\n── Step: Remove Orphan Person Nodes ──", flush=True)
    
    r = session.run("MATCH (p:Person) WHERE NOT (p)--() RETURN count(p) as cnt").single()
    count = r["cnt"]
    print(f"  Found {count} orphan Person nodes", flush=True)
    
    if count == 0:
        return 0
    
    if DRY_RUN:
        print(f"  DRY-RUN: Would delete {count} orphan Person nodes", flush=True)
        return 0
    
    session.run("MATCH (p:Person) WHERE NOT (p)--() DELETE p")
    print(f"  ✓ Removed {count} orphan Person nodes", flush=True)
    return count


def write_cleanup_report(before, after, actions_taken):
    """Write a markdown report of what was done."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    report = f"""# Neo4j Weekly Cleanup Report — {timestamp}

## Before / After

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Person nodes (total) | {before['person_total']} | {after['person_total']} | {after['person_total'] - before['person_total']:+d} |
| Person nodes (named) | {before['person_named']} | {after['person_named']} | {after['person_named'] - before['person_named']:+d} |
| Person null-name | {before['person_null_name']} | {after['person_null_name']} | {after['person_null_name'] - before['person_null_name']:+d} |
| Person orphans | {before['orphan_persons']} | {after['orphan_persons']} | {after['orphan_persons'] - before['orphan_persons']:+d} |
| Social Profiles | {before['social_profiles']} | {after['social_profiles']} | {after['social_profiles'] - before['social_profiles']:+d} |
| Relationships | {before['relationships']} | {after['relationships']} | {after['relationships'] - before['relationships']:+d} |

## Actions Taken

{chr(10).join(f'- {a}' for a in actions_taken)}

## Mode
{'DRY RUN — no changes made' if DRY_RUN else 'LIVE RUN — changes applied'}
"""
    return report


def main():
    print("🧹 Neo4j Weekly Cleanup starting...", flush=True)
    print(f"URI: {NEO4J_URI}", flush=True)
    if DRY_RUN:
        print("*** DRY RUN MODE — no changes will be made ***", flush=True)
    
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
    
    try:
        with driver.session() as session:
            # Metrics before
            print("\n── Before Metrics ──", flush=True)
            before = get_metrics(session)
            for k, v in before.items():
                print(f"  {k}: {v}", flush=True)
            
            actions_taken = []
            
            if not INDEXES_ONLY:
                # Step 1: Remove null-name Person nodes
                n1 = step_remove_null_name_persons(session)
                if n1 > 0:
                    actions_taken.append(f"Removed {n1} null-name Person nodes")
                
                # Step 2: Remove concept-as-person nodes
                n2 = step_remove_concept_persons(session)
                if n2 > 0:
                    actions_taken.append(f"Removed {n2} concept-as-Person nodes")
                
                # Step 3: Merge duplicates
                n3 = step_merge_duplicates_simple(session)
                if n3 > 0:
                    actions_taken.append(f"Merged/removed {n3} duplicate Person nodes")
                
                # Step 4: Remove orphans (post-cleanup)
                n4 = step_remove_orphan_persons(session)
                if n4 > 0:
                    actions_taken.append(f"Removed {n4} orphan Person nodes")
            
            # Step 5: Ensure indexes (always)
            n5 = step_ensure_indexes(session)
            if n5 > 0:
                actions_taken.append(f"Created {n5} new indexes")
            
            # Metrics after
            print("\n── After Metrics ──", flush=True)
            after = get_metrics(session)
            for k, v in after.items():
                diff = v - before[k]
                sign = "+" if diff >= 0 else ""
                print(f"  {k}: {v} ({sign}{diff})", flush=True)
            
            # Write report
            report = write_cleanup_report(before, after, actions_taken)
            report_path = f"/Users/debra/SecondBrain/Reflections/Daily/{datetime.now().strftime('%Y-%m-%d')} Neo4j Cleanup.md"
            with open(report_path, "w") as f:
                f.write(report)
            print(f"\nReport written to: {report_path}", flush=True)
            
            # Print summary
            print("\n🧹 Cleanup complete!", flush=True)
            total_removed = before["person_total"] - after["person_total"]
            print(f"   Person nodes: {before['person_total']} → {after['person_total']} ({total_removed:+d})", flush=True)
            print(f"   Actions taken: {len(actions_taken)}", flush=True)
            if not actions_taken:
                print("   (Graph is already clean)", flush=True)
    
    finally:
        driver.close()


if __name__ == "__main__":
    main()
