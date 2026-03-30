# Batman Killed the Ghost v5 - FINAL VERSION
## Build Plan

### APPROACH
1. Generate ONE anchor frame that defines ALL characters (Batman, Spider-Man, Ghost, Sparkles, Avie, Dad)
2. Use that anchor as image-to-image reference for EVERY subsequent frame
3. Match narration BEAT FOR BEAT - if she says "he looked up and saw them on the roof" the drawing SHOWS that
4. No animation. Pure slideshow with Ken Burns (slow zoom/pan). Audio carries it.
5. QA every frame before assembly. No shipping without review.

### STYLE
- Kid's crayon on white paper
- Stick figures with circle heads
- Batman = circle + two ear triangles + cape scribble
- Spider-Man = red/blue stick figure
- Ghost = white blob, two dot eyes
- Colors go outside the lines
- Scale is intentionally wrong (Batman bigger than house)
- Kid handwriting labels where needed
- Construction paper / crayon texture throughout

### TITLE CARD
"BATMAN KILLED THE GHOST"
"by Avie Abell (age 3)"
- crayon on black construction paper

### CHARACTERS (defined in anchor frame)
All on one sheet so Flux locks the style:
- Batman (black stick figure, triangle ears, yellow belt, cape)
- Spider-Man (red/blue stick figure, web pattern scribble)
- Ghost (white blob, dot eyes)
- Avie (small girl, brown hair, pajamas)
- Dad (bigger stick figure, sitting)
- Sparkle creatures (round glowing dots with tiny legs)
- Glowing Book (rectangle with evil face)

### FRAMES (17 total, matching screenplay timestamps)

| # | Time | Audio | Visual (MUST MATCH) |
|---|------|-------|---------------------|
| 1 | 0:00-0:03 | silence | Title: "BATMAN KILLED THE GHOST" / "by Avie Abell (age 3)" on black paper |
| 2 | 0:00-0:08 | Alex: "what was it called?" Avie: "Batman Killed the Ghost" | Avie in bed, dad on edge, warm lamp. She's excited, gesturing |
| 3 | 0:08-0:21 | "it was a very dark night" | Page scribbled dark. Just darkness. Two tiny white eyes peeking out |
| 4 | 0:21-0:32 | "Spider-Man and Batman killed a ghost on top of a roof" | House with Batman + Spider-Man ON ROOF, ghost flat with X eyes. Person sleeping inside (visible through wall) |
| 5 | 0:32-0:52 | "they looked up onto their roof and saw those guys. They flew into their house" | Person in bed LOOKING UP at ceiling. Batman + Spider-Man visible through hole in roof above. Then crashing into house |
| 6 | 0:52-1:02 | "the ghost was alive again" | Ghost popping back up with surprised face. Multiple ghosts appearing |
| 7a | 1:02-1:15 | "a glowing book came and scared Batman" | Floating glowing book with evil grin face. Batman cowering in terror |
| 7b | 1:15-1:27 | "Batman ran away over the fences back to his house" | Batman running/jumping over picket fences, cape flying, heading to tiny house |
| 8 | 1:27-1:40 | "that's the end. They happily lived ever again" | Batman peeking nervously from house window. Ghost waving outside. "they happily lived ever again" in kid writing |
| 9 | 1:40-2:04 | sequel pitches: Ghost Killed Batman, Spider-Man Killed Batman | Three mini movie poster panels, each more absurd than the last |
| 10 | 2:04-2:14 | "Magic Sparkles Trying to Get Other Sparkles" | New title card in rainbow crayon with sparkles and stars. Total tonal shift |
| 11 | 2:14-2:29 | "it was a night day. Sparkles came hopping in the forest" | Forest with sky split: half night/half day. Sparkle creatures hopping |
| 12 | 2:29-2:47 | "hopped hopped hopped trying to get the other ones" | Chase scene. Sparkles chasing other sparkles through forest |
| 13 | 2:47-3:00 | "the ghost tried to scare the sparkles" | SAME ghost from Story 1 appears! Sparkles scatter toward tiny house. Rain falling |
| 14 | 3:00-3:14 | "their moms and dads were so happy" | Sparkle family in cozy house. Baby sparkles in beds. Parent sparkles watching lovingly |
| 15 | 3:14-3:24 | "good night" | Back to bedroom. Avie falling asleep. Dream bubbles with all characters above her |
| 16 | +5s | silence | Credits: "Written and Directed by Avie Abell" / "Produced by Dad" / heart |

### GENERATION PLAN
1. Generate anchor frame with ALL characters on one sheet
2. Generate Frame 1 (title) - standalone, no reference needed
3. Generate Frames 2-16 using anchor as style reference (image-to-image)
4. QA: review every frame, regenerate any that don't match narration or break consistency
5. Assembly: ffmpeg slideshow with Ken Burns + crossfades, synced to audio timestamps
6. Final review before sending to Alex

### TECH
- Flux via fal.ai for image generation
- image-to-image mode with anchor reference
- ffmpeg for video assembly
- Audio: /Users/debra/Downloads/Batman Killed the Ghost.m4a
