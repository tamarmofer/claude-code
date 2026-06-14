# Motion & Color

## Color Systems

Define everything in CSS variables. Use `oklch()` for new work — it interpolates more naturally than HSL or RGB.

```css
:root {
  --bg: oklch(98% 0.01 90);
  --fg: oklch(20% 0.02 90);
  --accent: oklch(65% 0.18 35);   /* punch */
  --muted: oklch(50% 0.02 90);
  --line: color-mix(in oklch, var(--fg) 12%, transparent);
}

@media (prefers-color-scheme: dark) {
  :root {
    --bg: oklch(15% 0.02 250);
    --fg: oklch(95% 0.01 250);
    --line: color-mix(in oklch, var(--fg) 18%, transparent);
  }
}
```

**Heuristics:**
- One dominant background (90%), one ink color (8%), one punch accent (2%). Add a fourth only with intent.
- Generate hover states with `color-mix(in oklch, var(--accent) 80%, var(--bg))` — keeps tone consistent.
- For backgrounds, mesh gradients (`radial-gradient` stacked with `mix-blend-mode`) outperform linear gradients.

## Easing & Duration

Skip browser defaults. Curated curves:

```css
:root {
  --ease-out-quart: cubic-bezier(0.25, 1, 0.5, 1);
  --ease-out-expo: cubic-bezier(0.16, 1, 0.3, 1);
  --ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);   /* slight overshoot */
  --ease-vercel: cubic-bezier(0.32, 0.72, 0, 1);      /* snappy */
}
```

| Action | Duration | Easing |
|---|---|---|
| Hover (color/opacity) | 150ms | `--ease-out-quart` |
| Hover (transform) | 300ms | `--ease-out-expo` |
| Page transition | 500-700ms | `--ease-vercel` |
| Mount stagger | 80ms per item | `--ease-out-expo` |
| Spring (buttons, modals) | — | spring physics, not duration |

## CSS-only patterns

**Staggered reveal on page load:**
```css
.stagger > * {
  opacity: 0;
  translate: 0 12px;
  animation: rise 600ms var(--ease-out-expo) forwards;
}
.stagger > *:nth-child(1) { animation-delay: 0ms; }
.stagger > *:nth-child(2) { animation-delay: 80ms; }
.stagger > *:nth-child(3) { animation-delay: 160ms; }
@keyframes rise { to { opacity: 1; translate: 0 0; } }
```

**`@starting-style` for mount without JS:**
```css
.toast {
  opacity: 1; translate: 0 0;
  transition: opacity 300ms, translate 300ms var(--ease-out-expo);
  @starting-style { opacity: 0; translate: 0 8px; }
}
```

## React: Motion library

```tsx
import { motion } from "motion/react";

<motion.div
  initial={{ opacity: 0, y: 12 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
/>
```

Use Motion (formerly Framer Motion) for layout animations, gesture-driven UI, and view transitions. For pure mount/exit fades, prefer CSS.

## Reduced motion

Always honor user preference:

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```
