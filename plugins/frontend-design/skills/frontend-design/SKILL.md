---
name: frontend-design
description: This skill should be used when the user asks to "build a landing page", "design a UI", "create a hero section", "make a dashboard", "build a component", "style this page", "make a portfolio site", or any request to design or implement frontend interfaces (HTML, CSS, React, Vue). Produces distinctive, production-grade code with high design quality and avoids generic AI aesthetics.
license: Complete terms in LICENSE.txt
---

# Frontend Design

Create distinctive, production-grade frontend interfaces that avoid generic "AI slop" aesthetics. Implement working code with exceptional attention to aesthetic detail, motion, type, and color.

## Workflow

1. **Read the brief.** Pull purpose, audience, and any constraints (framework, performance, accessibility). If essential signal is missing (brand, target tone, must-use framework), ask once and proceed.
2. **Commit to one aesthetic direction** from `references/aesthetics.md`. Don't blend two. The most common failure is hedged eclecticism that reads as "AI default."
3. **Choose type and color** with concrete picks from `references/typography.md` and `references/motion-and-color.md`. Avoid Inter, Roboto, Space Grotesk, and purple-on-white gradients—those are AI-slop markers.
4. **Implement working code** (HTML/CSS, React, Vue, etc.) that is functional, accessible, and meticulously refined.
5. **Audit before finishing**: accessibility, reduced-motion, dark-mode parity, responsive behavior.

## Aesthetic Direction

Pick an extreme rather than a blend: brutalist, editorial, refined/luxury, retro-futuristic, soft/pastel, industrial, playful, etc. Each has a defined font stack, palette, and signature layout moves in `references/aesthetics.md`. If the brief doesn't dictate one, choose the **least obvious** direction that still fits the purpose.

Bold maximalism and refined minimalism both work—the key is intentionality, not intensity. Match implementation complexity to the vision: maximalist designs need elaborate code and effects; minimalist designs need precision in spacing, type, and detail.

## Typography

- Pair one distinctive display font with one refined body font (mono optional).
- Reach for foundries (Fontshare, Pangram Pangram, Klim) or curated Google Fonts.
- Use OpenType features: `font-feature-settings: "ss01", "salt"`, variable axes like `opsz`.

Concrete pairings per aesthetic direction in `references/typography.md`.

## Color & Theme

- Define everything in CSS variables. Use `oklch()` for new work—it interpolates more naturally than HSL.
- One dominant background (~90%), one ink color (~8%), one accent (~2%). Add a fourth only with intent.
- Dominant colors with sharp accents outperform timid, evenly-distributed palettes.
- Use `color-mix(in oklch, ...)` for hover states to keep tone consistent.

Palette templates and dark-mode patterns in `references/motion-and-color.md`.

## Motion

- Prefer CSS for mount/exit; reach for Motion (React) for layout animations, gestures, and view transitions.
- Curate easing—skip browser defaults. Use `cubic-bezier(0.16, 1, 0.3, 1)` (out-expo) for transforms; `cubic-bezier(0.32, 0.72, 0, 1)` (Vercel) for page transitions.
- One well-orchestrated page-load stagger creates more delight than scattered micro-interactions.
- Always honor `prefers-reduced-motion`.

Concrete snippets (staggered reveals, `@starting-style`, spring physics) in `references/motion-and-color.md`.

## Spatial Composition

- Unexpected layouts: asymmetry, overlap, diagonal flow, grid-breaking elements.
- Choose generous negative space *or* controlled density—not weak middle-ground.
- Use CSS Grid for compositions, Flexbox for component-internal flow.
- For wide screens, multi-column layouts with rule lines often beat single centered columns.

## Backgrounds & Detail

Create atmosphere rather than defaulting to solid colors:

- Mesh gradients (stacked `radial-gradient`s with `mix-blend-mode`) outperform linear gradients.
- Noise textures (subtle SVG noise overlays at 4-8% opacity) add depth.
- `box-shadow: 0 0 40px currentColor` for glow effects in retro-futuristic.
- Layered transparencies, decorative rules, custom cursors where the aesthetic supports them.

## Accessibility Floor

Non-negotiable on every output:

- WCAG AA contrast (4.5:1 body, 3:1 large text). Use `oklch()` lightness deltas to verify.
- Semantic HTML: `<button>` for actions, `<a>` for navigation, headings in order.
- Visible `:focus-visible` rings — never `outline: none` without a replacement.
- Keyboard navigation: tab order, escape closes modals, arrow keys in menus.
- `prefers-reduced-motion` honored.
- Alt text on meaningful images; `aria-label` on icon-only buttons.

## Anti-patterns

NEVER ship these AI-slop markers:

- Inter / Roboto / Open Sans / system-ui as a deliberate choice
- Purple gradients on white backgrounds
- Space Grotesk (overused — recognizable as "AI portfolio")
- Centered hero with one button and three feature cards
- Soft drop shadows on every card with `border-radius: 12px`
- Identical aesthetic across unrelated projects

Vary across generations: light vs dark, serif vs sans, dense vs sparse. No two outputs should converge on the same defaults.

## One-line directive

Default to one strong aesthetic commitment over hedged blends.

## Additional Resources

- `references/aesthetics.md` — seven aesthetic directions with font, palette, layout moves, and reference sites
- `references/typography.md` — concrete font pairings, loading snippets, OpenType features, hierarchy heuristics
- `references/motion-and-color.md` — oklch palettes, easing curves, CSS-only patterns, Motion (React) examples, reduced-motion handling
