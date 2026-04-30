# Puente AI — Brand Guide

> **Pay less. Move faster.** — Trade intelligence for the US–LATAM corridor.

This document is the **single source of truth** for Puente AI brand consistency across web, presentations, and marketing. All values are extracted directly from `src/index.css` and `tailwind.config.ts` — keep them in sync.

---

## 1. Typography

| Use | Family | Weights | Token / Class |
|---|---|---|---|
| Headings (H1–H6) | **Funnel Display** | 300–800 | `font-display` |
| Body / UI | **DM Sans** | 400, 500, 600, 700 | `font-body` (default on `<body>`) |
| Savings figures | DM Sans 700 | **56px** in `text-emerald` | Product rule — never override |

- Both families load from Google Fonts in `src/index.css`.
- **Rule:** never mix in a third family. If a piece needs accent, use weight or size within the two authorized families.

---

## 2. Brand Colors

| Name | HEX | HSL | CSS Token | Tailwind |
|---|---|---|---|---|
| **Gold (Primary)** | `#F9B405` | `43 96% 50%` | `--gold` / `--primary` | `bg-primary` |
| **Gold Light** | `#F7BB53` | `38 92% 65%` | `--gold-light` | `bg-gold-light` |
| **Dark Navy** | `#202836` | `217 26% 17%` | `--navy` | `bg-navy` |
| **Navy Light** | `#333C4C` | `217 20% 25%` | `--navy-light` | `bg-navy-light` |
| **Ocean (Teal)** | `#287AA3` | `200 60% 40%` | `--ocean` | `bg-ocean` |
| **Emerald (Savings)** | `#079667` | `160 91% 31%` | `--emerald` | `bg-emerald` |
| **Warm Amber** | `#F9B405` | `43 96% 50%` | `--warm-amber` | `bg-warm-amber` |
| **Amber Orange** | `#AB6C07` | `37 92% 35%` | `--amber-orange` | `bg-amber-orange` |
| **Danger Red** | `#DC2828` | `0 72% 51%` | `--danger-red` | `bg-danger-red` |

> **Rule:** never use HEX directly in components — always use the semantic token (`bg-primary`, `text-emerald`, etc.) so light/dark mode works automatically.

---

## 3. Semantic Tokens — Light vs Dark

| Token | Light | Dark |
|---|---|---|
| `--background` | `#F7F5F1` | `#0C1116` |
| `--foreground` | `#0E1629` | `#F8F9FA` |
| `--card` | `#FDFCFB` | `#111821` |
| `--popover` | `#FDFCFB` | `#111821` |
| `--muted` | `#F0EEE9` | `#1A222C` |
| `--muted-foreground` | `#6A717F` | `#7B899D` |
| `--border` | `#E5E1DA` | `#242C37` |
| `--input` | `#E5E1DA` | `#242C37` |
| `--primary` | `#F9B405` | `#FABB1E` |
| `--ring` | `#F9B405` | `#FABB1E` |
| `--destructive` | `#DC2828` | `#DC2828` |
| `--sidebar-background` | `#202836` | `#111721` |

- **Sidebar is always navy** in both modes.
- **Primary CTAs always use `--primary` (gold)** regardless of theme.

---

## 4. Brand Gradients & Effects

| Utility | Description |
|---|---|
| `text-gradient-gold` | Gold gradient for hero headlines (linear 135°: gold-light → gold → amber-orange) |
| `bg-gradient-gold` | Gold 135° fill for logo, premium CTAs, brand icons |
| `bg-gradient-navy` | Subtle vertical fade `background → card` |
| `bg-gradient-card` | Card with light 135° transparency for depth |
| `border-gold-subtle` | Gold border @ 20% opacity for soft emphasis |
| `glow-gold` | Gold box-shadow 30/60px for hover on cards & CTAs |
| `glass` | Glassmorphism: `backdrop-blur-xl + bg-card/80 + border-bottom` |
| `pill-pulse` | 2s pulse animation for processing states |

---

## 5. Shape System

| Token | Value |
|---|---|
| `--radius` | `0.75rem` (12px) — base for cards & buttons |
| `radius-lg` | `var(--radius)` |
| `radius-md` | `calc(var(--radius) - 2px)` |
| `radius-sm` | `calc(var(--radius) - 4px)` |

---

## 6. Layout

| Element | Value |
|---|---|
| Desktop sidebar | **240px fixed** · always navy |
| Container max | **1400px** (`2xl` breakpoint) |
| Container padding | `2rem` |
| Mobile breakpoint | `md:` 768px |
| Mobile nav | Bottom dock + central FAB for "New Analysis" |

---

## 7. Usage Map by Context

| Context | Token / Class |
|---|---|
| Primary CTAs | `bg-primary` (gold) over navy or cream |
| Sidebar / fixed nav | `bg-sidebar` (navy) + `text-sidebar-foreground` |
| **Savings figures** | `text-emerald` · **56px bold** · unbreakable rule |
| Success states (`compliance ✓`, `routed ✓`) | `text-emerald` / `bg-emerald` |
| Processing states | Navy with `pill-pulse` class |
| Errors | `bg-danger-red` |
| LATAM / warmth accents | `warm-amber` / `amber-orange` |
| Trust signals (footer) | `text-muted-foreground` + subtle icons |

---

## 8. UX Rules (non-negotiable)

- **'New Analysis' CTA** must be reachable within **2 clicks** from anywhere in the app.
- **Savings number** is the visual anchor of the results screen — 56px, emerald, never demoted.
- **Fallback** to hardcoded `DEMO_ANALYSIS` / `DEMO_ROUTING` if the backend API fails — never show a blank state.
- **Trust signals** (E2E encryption, corridor verification) always present in the footer.

---

## 9. Brand Voice

| Attribute | Value |
|---|---|
| Tagline | **Pay less. Move faster.** |
| Tone | Trustworthy like a bank, warm like a Miami neighbor. |
| Languages | EN / ES / PT — preserve proper nouns and locations in their original language (e.g., *Tejidos Medellín*, *São Paulo*). |
| Positioning | Trade intelligence layer for the US–LATAM corridor. |
| **What we are NOT** | A bank · a money transmitter · we do **not** move funds. |
| Target persona | **Maria** — bilingual SME owner in Miami, non-technical, $500K–$5M/year in imports. |

### Copy do's & don'ts

- ✅ Plain language: *"Fraud Score"*, not *"Risk Assessment Matrix"*.
- ✅ Dollar figures, not percentages, when possible (*"You save $1,240"*, not *"You save 4.2%"*).
- ✅ Bilingual labels for **critical financial terms only** — don't dual-label every UI string.
- ❌ No fabricated customers, no claimed licenses we don't have.
- ❌ Don't say *"verified supplier"* unless the documents support it.

---

## 10. Logo

- **Mark:** abstract bridge-arc forming a stylized **"P"**.
- **Wordmark:** `PUENTE AI` in Funnel Display Bold, tracking-tight.
- **On dark backgrounds:** use the white logo asset masked with `bg-gradient-gold` (see `AppSidebar.tsx`).
- **On light backgrounds:** use the color logo asset directly.
- **Minimum clear space:** equal to the height of the "P" mark on all sides.

---

## 11. File References

| Concern | File |
|---|---|
| Color tokens, gradients, fonts | `src/index.css` |
| Tailwind theme & color mapping | `tailwind.config.ts` |
| Bilingual copy (EN/ES/PT) | `src/lib/i18n.tsx` |
| SEO / Open Graph defaults | `index.html`, per-page `<Helmet>` |
| Logo assets | `src/assets/puente-logo*.png`, `puente-icon-color.png` |

---

© Puente AI · Brand Guide v1 · Generated from source code. Update this file whenever `index.css` or `tailwind.config.ts` change.
