# Design Decisions — abellminded.com

## MOOD: Cerebral Laboratory

The guiding metaphor is **a brilliant person's mind made visible** — not a portfolio site, not a marketing page. The brain map IS the experience. Everything else (About, Connect) exists as aftermath.

The dark palette, scanline animation, monospace type details, and subtle grain work together to say: *you're looking at something that thinks*. Mad scientist's lab, beautiful.

## PALETTE: Dark Luxury + Electric Singular

- **`#080808`** — Near-black (not pure `#000`, which reads flat). Deep enough to feel like space.
- **`#F5F0E8`** — Warm off-white. Not clinical gray-white. Warm like paper.
- **`#FF0080`** — The only color. Hot magenta. Used exactly once in the UI palette, so every use of it registers. Matches HeyDebra brand for continuity. Used on: accent rules, active nodes, panel decorations, status dots, CTA elements.
- No blue. No purple. No gradients.

## SIGNATURE MOVES

**1. The Living Brain Map as Hero**  
D3.js force-directed graph with 7 nodes. The graph breathes (edge opacity animation), nodes pulse (CSS `keyframes pulseOut`), and the simulation runs continuously with gentle forces keeping nodes in view. Clicking a node triggers the panel AND highlights connected nodes/edges — the graph becomes a navigation system.

**2. The Scanline**  
A single hot-pink 1px line sweeps the entire page every 14 seconds. Laboratory equipment. Barely noticeable but subliminally building the "this thing is alive" feeling.

**3. Custom Cursor**  
6px magenta dot + 28px ring with lag. Grows on hover over nodes. Eliminates the generic browser cursor entirely — signals this is a designed experience from frame one.

**4. Bebas Neue for Display**  
Compressed, uppercase, high-impact. Feels editorial (Interview Magazine) meets technical (NASA manual). NOT Inter. NOT Helvetica. The giant `ALEX ABELL` in the bottom-left of the hero is treated as a graphic element, not a headline.

**5. Outlined Text (Stroked)**  
`-webkit-text-stroke` used on `THE MIND BEHIND` and `BUILD` in the connect section. Hollow letters are a signature of VOUS Church, Chiara Luzzana, and other Awwwards nominees. Creates visual tension between filled and outlined type at the same size.

**6. Non-traditional Layout**  
- Hero: no center-align, no CTA. The graph IS the hero. Name is pinned bottom-left, small.
- About: sticky left / scrolling right. Asymmetric grid, not cards.
- Connect: oversized display type (`12vw`) with one ghost-text word. Not a contact form.

## ANTI-PATTERNS AVOIDED

- ❌ Blue-purple gradient → ✅ Solid `#080808` with grain texture
- ❌ Card grid → ✅ Asymmetric two-column about layout + numbered list
- ❌ Centered hero → ✅ Force-directed graph + bottom-left name
- ❌ Generic hover → ✅ Custom cursor + 3D node state changes + fill-wipe buttons
- ❌ Box shadows everywhere → ✅ No shadows; borders and glows only
- ❌ Inter/Helvetica → ✅ Bebas Neue (display) + Space Mono (labels/meta) + DM Sans (body)

## TYPOGRAPHY SYSTEM

| Role | Font | Treatment |
|---|---|---|
| Display / Hero | Bebas Neue | Giant, compressed, uppercase |
| Labels / Meta | Space Mono | Tiny, tracked, uppercase — feels technical |
| Body | DM Sans | Light (300) weight, generous line-height |

All body/display sizes use `clamp()` for fluid scaling. No fixed `px` type sizes.

## MOTION

- **Node pulse**: `scale(1) → scale(2.6)` ring with `opacity 0 → 0.45 → 0` on infinite loop. Staggered timing per node.
- **Edge breathe**: Opacity oscillates 0.1 → 0.22 over 4.5s. All edges, offset by index.
- **Active edge**: Animated `stroke-dashoffset` (flowing dashes) when a node is selected.
- **Panel**: `translateX(100%) → 0` slide, 600ms with custom ease.
- **Scanline**: Full-height sweep every 14s.
- **Scroll reveals**: `IntersectionObserver` + `translateY(2rem) → 0` entrance.
- **Cursor ring**: Lerp-based lag (18% catch-up per frame).

All animations respect `prefers-reduced-motion`.

## DECISIONS NOT MADE

- **No page transitions** — single-page, no routes needed.
- **No loading screen** — the graph bootstraps fast enough; a loader would add pretension without payoff.
- **No Three.js / WebGL** — D3 SVG is sufficient and loads without a multi-MB dependency.
- **No dark mode toggle** — the design IS the dark mode. It's not a preference, it's the brand.
