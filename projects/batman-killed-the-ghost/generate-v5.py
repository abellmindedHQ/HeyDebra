#!/usr/bin/env python3
"""
Batman Killed the Ghost v5 - Image Generation
Generates anchor frame first, then all 17 frames using anchor as style reference.
"""

import os
import sys
import json
import time
import base64
import urllib.request
import fal_client

os.environ['FAL_KEY'] = '9bce9a0b-28b1-42e4-97be-c7c0ecd8dc8b:41498985bbc7b896baa1ea1019487fb0'

FRAMES_DIR = '/Users/debra/.openclaw/workspace/projects/batman-killed-the-ghost/frames-v5'
os.makedirs(FRAMES_DIR, exist_ok=True)

STYLE_BASE = (
    "children's crayon drawing on white paper, stick figures with circle heads, "
    "wobbly lines, scribble coloring outside the lines, intentionally wrong scale, "
    "kid handwriting labels, construction paper texture, bright crayon colors, "
    "charming childlike art, age 3 drawing style"
)

# ─── ANCHOR FRAME ─────────────────────────────────────────────────────────────
ANCHOR_PROMPT = (
    f"{STYLE_BASE}. "
    "Character reference sheet showing ALL characters from the story arranged on one white page: "
    "1) Batman - black stick figure with triangle bat ears, yellow belt scribble, and a wobbly cape drawn in black crayon. Label says 'Batman' in kid writing. "
    "2) Spider-Man - red and blue stick figure with messy web lines scribbled on, round head, stick arms out. Label says 'Spider-Man'. "
    "3) Ghost - simple white blob shape with two black dot eyes and a squiggly mouth. Label says 'Ghost'. "
    "4) Avie - tiny girl stick figure, brown scribble hair, pajama dress, big smile. Label says 'Avie (me)'. "
    "5) Dad - taller stick figure, sitting down, simple smile. Label says 'Dad'. "
    "6) Sparkle Creatures - round glowing cotton-ball shapes with tiny stick legs and dot eyes, sparkle lines around them. Label says 'Sparkles'. "
    "7) Glowing Evil Book - rectangle with evil crayon grin face and squiggly glow lines. Label says 'Scary Book'. "
    "All characters are arranged in a grid on white paper background. "
    "Each is drawn with thick crayon marks. Colors go outside the lines. Scale is inconsistent. "
    "This is clearly drawn by a 3-year-old but with maximum charm."
)

# ─── FRAME PROMPTS ────────────────────────────────────────────────────────────
FRAMES = [
    {
        "id": "frame00_anchor",
        "label": "Character Anchor Sheet",
        "prompt": ANCHOR_PROMPT,
        "is_anchor": True,
    },
    {
        "id": "frame01_title",
        "label": "Title Card",
        "prompt": (
            f"{STYLE_BASE}. "
            "Title card on BLACK construction paper. "
            "Big wobbly crayon letters in white and yellow that say 'BATMAN KILLED THE GHOST'. "
            "Below that in smaller kid writing: 'by Avie Abell (age 3)'. "
            "Tiny stick figure Batman in corner with triangle ears and cape. "
            "Tiny ghost blob in other corner with dot eyes. "
            "White chalk/crayon on black paper texture. Scruffy kid writing, letters uneven."
        ),
    },
    {
        "id": "frame02_bedtime",
        "label": "Bedtime storytelling",
        "prompt": (
            f"{STYLE_BASE}. "
            "Cozy bedroom at night. Warm yellow lamplight. "
            "Small girl stick figure with brown scribble hair tucked in bed with lumpy pillow and blanket. "
            "Dad stick figure sitting on edge of bed, bigger than the girl. "
            "Girl's arms are raised up excitedly (wavy lines for excitement). "
            "Stuffed animal blob shapes on the bed. "
            "Window with moon and stars outside, drawn in yellow crayon. "
            "Warm orange/yellow background in the room. Text 'bedtime!' in kid writing."
        ),
    },
    {
        "id": "frame03_darknight",
        "label": "Very dark night",
        "prompt": (
            f"{STYLE_BASE}. "
            "Page covered in HEAVY dark blue and black crayon scribbles - very dark night. "
            "Just darkness, thick crayon marks covering entire background. "
            "Only two tiny white dot eyes visible peeking out from the darkness. "
            "Scattered white crayon stars that are just plus-sign shapes. "
            "Text 'very dark!' written in white crayon. "
            "Extremely dark and moody for a kid drawing but still charming."
        ),
    },
    {
        "id": "frame04_rooftop",
        "label": "Spider-Man and Batman kill ghost on roof",
        "prompt": (
            f"{STYLE_BASE}. "
            "House drawing - rectangle body, triangle roof, two square windows. "
            "ON TOP OF THE ROOF: Batman stick figure (black with triangle ears, yellow belt) standing triumphantly. "
            "Spider-Man stick figure (red and blue, scribbled web lines) standing next to Batman. "
            "Ghost blob (white with X eyes - it's dead) lying flat on the roof. "
            "INSIDE THE HOUSE visible through a window: person stick figure lying horizontal in bed with 'Z' floating above. "
            "Night sky background with scribbled stars and moon. "
            "Batman and Spider-Man have arms raised. Text 'gotcha!' near ghost."
        ),
    },
    {
        "id": "frame05_lookedup",
        "label": "They looked up and saw them",
        "prompt": (
            f"{STYLE_BASE}. "
            "Inside view of a house bedroom. "
            "Person stick figure sitting up in bed with head tilted WAY back, looking up at ceiling. "
            "Their eyes are huge circles, totally surprised. "
            "Above, a big HOLE in the ceiling (jagged crayon lines). "
            "Through the hole: Batman stick figure and Spider-Man stick figure peering down from the roof, visible against night sky. "
            "Ghost blob also peering down through hole. "
            "Action lines showing them crashing/falling into the house. "
            "Text 'THEY SAW THEM!!' in kid writing. Stars and moon visible through hole."
        ),
    },
    {
        "id": "frame06_ghostalive",
        "label": "Ghost was alive again",
        "prompt": (
            f"{STYLE_BASE}. "
            "Ghost blob character is now alive again! "
            "Ghost has big surprised happy eyes (circles with dots) and a wide crayon smile. "
            "Sparkle lines / asterisks radiating around the ghost showing it is glowing and alive. "
            "Multiple smaller ghost blobs appearing behind the main ghost. "
            "Furniture in the room is knocked over (crooked rectangle table, wobbly chair). "
            "Text 'ALIVE AGAIN!!' written in excited kid letters. "
            "Main ghost has arms raised in victory (stick arms up)."
        ),
    },
    {
        "id": "frame07a_glowingbook",
        "label": "Glowing book scares Batman",
        "prompt": (
            f"{STYLE_BASE}. "
            "Dark night background, heavy black/dark blue crayon scribbles. "
            "FLOATING BOOK in center: rectangle shape, yellow/orange glow scribbled around it, "
            "evil grin face drawn on cover (curved line mouth, dot eyes, eyebrows drawn down mean). "
            "Lots of yellow scribble lines radiating out = scary glow. "
            "Batman stick figure on the right side: triangle ears, black crayon body, "
            "arms up in terror position, HUGE circle eyes, wavy fear lines around him. "
            "Text 'SCARY BOOK!!' and 'aaaaaa!' in kid writing. "
            "Batman is clearly terrified."
        ),
    },
    {
        "id": "frame07b_batmanruns",
        "label": "Batman runs away over fences",
        "prompt": (
            f"{STYLE_BASE}. "
            "Batman stick figure RUNNING to the right, leaning forward, legs spread in running pose. "
            "Cape is a big jagged scribble behind him flying in the wind. "
            "Speed lines coming off Batman showing fast running. "
            "Three white picket fences - simple I-shapes in a row that he is jumping over. "
            "One fence he is mid-jump over. "
            "Tiny house in the far right distance (small rectangle with triangle roof). "
            "Night sky background. "
            "Text 'RUN BATMAN RUN!!' in big excited kid letters. "
            "Batman looks panicked, looking back over shoulder with scared expression."
        ),
    },
    {
        "id": "frame08_happily",
        "label": "Happily lived ever again",
        "prompt": (
            f"{STYLE_BASE}. "
            "Left side: Batman stick figure inside tiny house, peeking nervously out window. "
            "Only his ears (triangles) and eyes (big circles) visible through window frame. "
            "Right side: Ghost blob standing outside the house, waving with a stick arm. "
            "Ghost has happy dot eyes and curved smile. "
            "Night sky with stars and moon. "
            "Bottom of page in big wobbly kid handwriting: 'they happily lived ever again' "
            "(intentional no punctuation, slightly misspelled look). "
            "Heart drawn nearby. Flowers growing outside house in scribble green."
        ),
    },
    {
        "id": "frame09_sequels",
        "label": "Sequel pitches",
        "prompt": (
            f"{STYLE_BASE}. "
            "Three movie poster panels side by side on white paper, each a rough rectangle frame. "
            "Panel 1 - 'THE GHOST KILLED BATMAN': ghost blob standing over fallen Batman stick figure. "
            "Panel 2 - 'BATMAN KILLED THE GHOST': Batman with arms raised over ghost with X eyes. Gold star sticker drawn on this one. "
            "Panel 3 - 'SPIDER-MAN KILLED BATMAN': Spider-Man standing triumphant over fallen Batman. "
            "Each title written in wobbly crayon letters across the top of each panel. "
            "Each panel has different colored crayon border. "
            "Text 'coming soon!!' across the top. Very dramatic, absurd, funny."
        ),
    },
    {
        "id": "frame10_sparkletitle",
        "label": "Magic Sparkles title card",
        "prompt": (
            f"{STYLE_BASE}. "
            "Title card on LIGHT BLUE or PINK construction paper. "
            "Rainbow crayon letters spelling 'MAGIC SPARKLES' - each letter a different color. "
            "Below in kid writing: 'Trying to Get Other Sparkles'. "
            "Stars of all sizes scattered everywhere, drawn as asterisks and plus signs in silver/gold/yellow. "
            "Round glowing sparkle creatures (cotton ball shapes with dot eyes) bouncing around the title. "
            "Hearts, sparkle bursts, and glitter effects drawn with gold/silver crayon. "
            "Total tonal shift from Batman - this is pure MAGIC and sparkle energy. "
            "Very colorful and joyful."
        ),
    },
    {
        "id": "frame11_nightday",
        "label": "Night day forest - Sparkles hopping",
        "prompt": (
            f"{STYLE_BASE}. "
            "Magical forest scene. Sky is split diagonally - "
            "LEFT HALF: dark blue night sky with white crayon stars and crescent moon. "
            "RIGHT HALF: bright yellow daytime sky with a big wobbly sun. "
            "The two halves meet in a diagonal line across the sky (this is a 'night day'). "
            "Green crayon trees (lollipop shapes - circles on sticks). "
            "Forest floor is green scribble grass. "
            "Multiple round sparkle creatures hopping through the forest - "
            "each is a white or golden blob with dot eyes and tiny stick legs and sparkle lines around it. "
            "Text 'night day!!' and 'it glowed!' in kid writing."
        ),
    },
    {
        "id": "frame12_hoppedhopped",
        "label": "Sparkles chase scene",
        "prompt": (
            f"{STYLE_BASE}. "
            "Forest chase scene! "
            "Group of 3 sparkle creatures (round glowing blobs with stick legs) on the left, hopping TOWARD the right. "
            "Their legs are in running position, motion lines behind them. "
            "Group of 2 sparkle creatures on the right looking BACK with wide scared eyes, running away. "
            "Rainbow colored trails streak behind all the sparkles. "
            "Trees rushing past - green lollipop trees tilted slightly with speed lines. "
            "Text 'hopped hopped hopped!!' in bouncy kid letters. "
            "Arrows and motion lines everywhere showing energetic movement. "
            "Everything is colorful and silly."
        ),
    },
    {
        "id": "frame13_ghostscares",
        "label": "Ghost tries to scare sparkles - rainy day",
        "prompt": (
            f"{STYLE_BASE}. "
            "Forest scene with gray crayon clouds above. "
            "Rain falling - blue vertical lines all over the scene. "
            "The SAME ghost blob from Story 1 pops out from behind a tree - "
            "it has its arms raised trying to be scary, wide eyes, wavy ghost edges. "
            "Text 'BOO!' in big letters near the ghost. "
            "Multiple sparkle creatures are SCATTERING in all directions, "
            "bouncing/running away from ghost, motion lines behind them. "
            "In the far background: tiny glowing house - rectangle with light in windows. "
            "Text 'rainy day!' and 'run away!!' in kid writing. "
            "Crossover episode energy - same ghost different story."
        ),
    },
    {
        "id": "frame14_momsanddads",
        "label": "Moms and dads are happy",
        "prompt": (
            f"{STYLE_BASE}. "
            "Inside cozy glowing house. Warm yellow/orange interior. "
            "Three or four small sparkle creature blobs tucked into tiny beds - "
            "each bed is a rectangle with a blanket blob on top. "
            "Two BIGGER sparkle creatures standing nearby - one with a tiny bow scribble (mom), "
            "one with a tiny hat scribble (dad). Both have big happy curved-line smiles. "
            "Pink hearts floating above everyone. "
            "Windows show dark night outside with stars. "
            "Text 'so happy!!' and 'good night little sparkles' in kid writing. "
            "The warmest, most cozy, wholesome crayon drawing ever. "
            "Everything glows softly with yellow."
        ),
    },
    {
        "id": "frame15_goodnight",
        "label": "Good night - back to bedroom",
        "prompt": (
            f"{STYLE_BASE}. "
            "Return to cozy bedroom from beginning. "
            "Same small girl stick figure with brown scribble hair, now sleepy - "
            "eyes are closed curved lines (sleeping eyes), tiny smile. "
            "Dad stick figure leaning over her, tucking in blanket. "
            "DREAM BUBBLES floating above her head in a cloud shape: "
            "inside the bubbles are tiny versions of all the characters: "
            "mini Batman with triangle ears, mini ghost blob, mini Spider-Man, "
            "mini sparkle creatures, tiny glowing book. "
            "All the dream characters are sleeping too (Z's floating). "
            "Stars and moon outside the window. "
            "Text 'good night' in very sleepy-looking droopy kid letters."
        ),
    },
    {
        "id": "frame16_credits",
        "label": "End credits",
        "prompt": (
            f"{STYLE_BASE}. "
            "Credits card on BLACK construction paper like the title card. "
            "White/yellow crayon text in wobbly kid writing: "
            "Line 1: 'Written and Directed by Avie Abell' "
            "Line 2: 'Produced by Dad' "
            "Line 3 smaller: 'No Batmans were harmed' "
            "Line 4: 'They happily lived ever again.' "
            "Big red crayon heart at the bottom. "
            "Small star doodles in corners. "
            "Simple, charming, perfect ending card."
        ),
    },
]


def download_image(url, path):
    """Download image from URL to path."""
    urllib.request.urlretrieve(url, path)
    print(f"  ✓ Saved: {path}")


def generate_image(prompt, output_path, reference_image_path=None, retries=2):
    """Generate image using fal.ai flux."""
    
    for attempt in range(retries + 1):
        try:
            if reference_image_path and os.path.exists(reference_image_path):
                # Image-to-image with anchor reference
                with open(reference_image_path, 'rb') as f:
                    img_b64 = base64.b64encode(f.read()).decode()
                img_url = f"data:image/jpeg;base64,{img_b64}"
                
                result = fal_client.run(
                    "fal-ai/flux/dev/image-to-image",
                    arguments={
                        "prompt": prompt,
                        "image_url": img_url,
                        "strength": 0.92,  # High strength = follow prompt mostly, just use anchor for style cues
                        "num_inference_steps": 28,
                        "guidance_scale": 3.5,
                        "num_images": 1,
                        "image_size": "landscape_16_9",
                        "enable_safety_checker": False,
                        "output_format": "jpeg",
                    }
                )
            else:
                # Text-to-image (for anchor and title cards)
                result = fal_client.run(
                    "fal-ai/flux/dev",
                    arguments={
                        "prompt": prompt,
                        "num_inference_steps": 28,
                        "guidance_scale": 3.5,
                        "num_images": 1,
                        "image_size": "landscape_16_9",
                        "enable_safety_checker": False,
                        "output_format": "jpeg",
                    }
                )
            
            images = result.get("images", [])
            if images:
                img_url = images[0]["url"]
                download_image(img_url, output_path)
                return True
            else:
                print(f"  ✗ No images in result: {result}")
                
        except Exception as e:
            print(f"  ✗ Attempt {attempt+1} failed: {e}")
            if attempt < retries:
                time.sleep(5)
    
    return False


def main():
    anchor_path = os.path.join(FRAMES_DIR, "frame00_anchor.jpg")
    
    # Which frames to generate (can pass frame IDs as args to regenerate specific ones)
    target_frames = sys.argv[1:] if len(sys.argv) > 1 else None
    
    for frame in FRAMES:
        frame_id = frame["id"]
        output_path = os.path.join(FRAMES_DIR, f"{frame_id}.jpg")
        
        # Skip if already exists (unless specifically targeted)
        if os.path.exists(output_path) and target_frames and frame_id not in target_frames:
            print(f"⏭  Skipping {frame_id} (exists)")
            continue
        
        if target_frames and frame_id not in target_frames:
            continue
            
        if os.path.exists(output_path) and not target_frames:
            print(f"⏭  Skipping {frame_id} (exists, use frame ID arg to regen)")
            continue
        
        print(f"\n🎨 Generating: {frame_id} - {frame['label']}")
        
        # Use anchor reference for all non-anchor, non-title frames
        use_anchor = (
            not frame.get("is_anchor") 
            and frame_id not in ["frame01_title", "frame10_sparkletitle", "frame16_credits"]
            and os.path.exists(anchor_path)
        )
        
        ref = anchor_path if use_anchor else None
        if ref:
            print(f"  📎 Using anchor reference")
        
        success = generate_image(frame["prompt"], output_path, ref)
        
        if success:
            print(f"  ✅ {frame_id} done")
        else:
            print(f"  ❌ {frame_id} FAILED")
        
        # Brief pause between API calls
        time.sleep(2)
    
    print("\n✨ Generation complete!")
    print(f"Frames in: {FRAMES_DIR}")


if __name__ == "__main__":
    main()
