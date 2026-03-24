# v0 Prompt: abellminded.com Redesign

## Paste this into v0.dev

Build a stunning single-page website for "abellminded" — a personal brand and innovation studio. This needs to feel like a premium, award-winning creative studio site. Think: the visual quality of Linear's marketing site meets the mystique of a Christopher Nolan film.

### Landing Section
- Full viewport height
- The word "abellminded" centered, massive typography
- "abell" in light weight, "mind" as the interactive trigger (subtle glow on hover), "ed" in light weight
- Below: tagline "building the future, one wild idea at a time" in muted small caps
- Subtle background: very faint constellation/neural network pattern, barely visible, slowly drifting
- Dark theme (#0a0e1a background, cream/white text)
- Font: something premium — Inter, Neue Haas, or Sora

### The Mind Graph (revealed on click of "mind")
- When user clicks "mind" in the title, the page transforms:
  - Title shrinks and moves to top-left corner
  - A beautiful 3D force-directed graph fills the viewport
  - Use Three.js or react-three-fiber for WebGL rendering
  - Nodes are glowing orbs with soft bloom/glow effects
  - Edges are luminous lines with varying thickness (more connections = thicker)
  - Nodes pulse gently, like neurons firing
  - Camera slowly orbits the graph
  - On hover: node expands slightly, shows label + type in a glassmorphism tooltip
  - On click: zooms to node, shows detail card

### Graph Nodes (data)
```
- abellminded (brand, largest, purple #7c5cfc)
- Mirror (product, large, amber #f59e0b) — "consciousness expansion system"
- Second Brain (engine, large, green #5cfcb0) — "knowledge capture pipeline"
- Pools (product, large, cyan #06b6d4) — "interest-based networks"
- HeyDebra (project, medium, pink #fc5c8c) — "AI companion framework"
- ORNL (work, medium, orange #fc8c5c) — "transformation leadership"
- Lunchpool (past, small, gray #666) — "where it started"
- The Sentinel (component, small, red #ef4444)
- The Silvering (component, small, silver #c0c0c0)
- The Looking Glass (component, small, gold #f59e0b)
- The Registry (component, small, blue #3b82f6)
- Night Swimming (system, small, indigo #6366f1)
- Neo4j (tech, tiny, blue #5c9cfc)
- Obsidian (tech, tiny, purple #9c5cfc)
- Knoxville (place, small, warm #fcb05c)
- Human Connection (theme, medium, pink #fc5ce0)
- AI (theme, medium, violet #b05cfc)
- Data Sovereignty (theme, small, green #22c55e)
```

### Graph Edges
```
abellminded → Mirror, Second Brain, Pools, HeyDebra, ORNL, Lunchpool
Mirror → Second Brain, The Sentinel, The Silvering, The Looking Glass, The Registry, AI, Human Connection
Second Brain → Neo4j, Obsidian, Night Swimming, AI
Pools → Lunchpool, Human Connection, Data Sovereignty
HeyDebra → AI, Second Brain
ORNL → Knoxville, AI
Lunchpool → Knoxville, Human Connection
```

### Visual Quality Requirements
- Bloom/glow post-processing on nodes
- Smooth 60fps animation
- Depth of field effect (nodes further from camera are slightly blurred)
- Particle dust floating in the background
- Edge lines should have a subtle animated flow (like data traveling along them)
- When transitioning from landing to graph: cinematic zoom effect, 1.5s ease
- Mobile responsive: graph still works on touch, pinch to zoom
- Back button (top-left, minimal) returns to landing with reverse animation

### Footer
- Small, muted: "♪ what is he building in there?" (Tom Waits reference)
- Clicking it opens a coming-soon page or the Notion roadmap

### Color Palette
- Background: #0a0e1a (deep navy-black)
- Primary: #7c5cfc (electric purple)
- Accent: #f59e0b (warm amber)
- Success: #22c55e (green)
- Text: #f8fafc (near-white)
- Muted: #64748b (slate)
- Card backgrounds: glassmorphism (rgba(255,255,255,0.05) with backdrop-blur)

### Tech
- React + Vite
- Three.js or react-three-fiber for 3D graph
- @react-three/postprocessing for bloom/glow
- Framer Motion for transitions
- Tailwind CSS for layout

### Vibe
This is the digital front door of a visionary's mind. It should feel like peering into something alive — a brain that's always thinking, always connecting. Not corporate. Not startup-bro. Thoughtful, mysterious, beautiful. The kind of site where someone screenshots it and shares it because it's just that cool.
