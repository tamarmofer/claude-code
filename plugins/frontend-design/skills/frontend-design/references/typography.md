# Typography

Distinctive font choices anchor a design. Reach for foundries (Fontshare, Pangram Pangram, GT Foundry, Klim, ABC Dinamo) or curated Google Fonts—not system defaults.

## Avoid

- Inter, Roboto, Open Sans, Helvetica, Arial, system-ui — generic AI defaults.
- Space Grotesk — overused. Recognizable as an "AI portfolio" font.
- Purple-gradient + Inter on white — the most clichéd combo.

## Concrete pairings (display + body)

| Aesthetic | Display | Body | Mono |
|---|---|---|---|
| Editorial / magazine | PP Editorial New, Fraunces, Tobias | Söhne, Mona Sans, Inter Tight | JetBrains Mono |
| Brutalist / raw | Neue Haas Grotesk Display, Druk, Migra | IBM Plex Mono, Space Mono | Space Mono |
| Refined / luxury | Cormorant Garamond, Reckless, Recoleta | Söhne, GT America | — |
| Retro-futuristic | Aspekta, Mona Sans, Test Signifier | Mona Sans, Aspekta | Berkeley Mono |
| Soft / pastel | Instrument Serif, Caslon Doric, Garet | General Sans, Switzer | — |
| Playful / toy-like | Boldonse, Hubot Sans, Migra Italic | Switzer, General Sans | — |
| Industrial / utilitarian | GT America Mono, Neue Machina | IBM Plex Sans | IBM Plex Mono |

## Loading

**Fontshare** (free for commercial use):
```html
<link href="https://api.fontshare.com/v2/css?f[]=satoshi@400,700&display=swap" rel="stylesheet">
```

**Google Fonts:**
```html
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,700&family=Inter+Tight:wght@400;600&display=swap" rel="stylesheet">
```

## OpenType features

Unlock optical sizing, alternates, and stylistic sets that elevate type quality:

```css
.heading {
  font-family: "Fraunces", serif;
  font-feature-settings: "ss01", "ss02", "salt", "liga";
  font-variation-settings: "opsz" 144, "SOFT" 50, "WONK" 1;
}
.body { font-feature-settings: "ss01", "cv11"; }
```

## Hierarchy heuristics

- One display family + one body family is plenty. A third (mono) only when needed.
- Use **size** and **weight** for hierarchy; resist using **color** as the primary signal.
- Tighten tracking on large display sizes (`letter-spacing: -0.03em`), loosen on small caps (`+0.08em`).
- For serifs: enable optical sizing (`font-variation-settings: "opsz" auto`) when the family is variable.
