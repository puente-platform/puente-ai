# DESIGN.md - Puente AI Specification

## 1. Product Intent & Persona
**Puente AI** is a trade intelligence platform connecting Miami-based LATAM importers with efficient payment routing, fraud scoring, and compliance checks.
- **Primary Persona:** Maria (35–55), bilingual, non-technical, managing $500K–$5M/year import business.
- **Tone:** "Trustworthy like a bank, warm like a Miami neighbor." Competent, helpful, not "cold fintech."

## 2. Information Architecture
- **Dashboard (`/`)**: High-level overview, KPIs, and recent activity.
- **New Analysis (`/analyze`)**: Core 3-step workflow (Upload -> Process -> Results).
- **Transaction History (`/transactions`)**: Searchable record of all previous analyses.
- **Settings (`/settings`)**: Profile and Language preferences.

## 3. Screen-by-Screen UX Spec
### Dashboard
- 4 KPI cards (Transfers, Saved, Risk, Pending).
- Recent Transactions table with backend-mapped status chips.
- Right sidebar: "New Analysis" CTA and Corridor Breakdown chart.
### New Analysis (Core Flow)
- **Step 1:** Large dashed upload zone (Deep Teal).
- **Step 2:** Horizontal 4-node pipeline with pulse animations.
- **Step 3:** The "Money Screen." Features the **visually dominant savings figure (56px Emerald)** and three detailed result cards (Fraud, Compliance, Payment Recommendation).
### Transaction History
- Filterable table with inline expansion to view full analysis results.
### Settings
- Simple two-column layout with a prominent EN/ES toggle.

## 4. Design Tokens
- **Colors:**
  - `dark-navy`: `#0A1628` (Sidebar, Headers)
  - `deep-teal`: `#0D7F7F` (CTAs, Routing)
  - `emerald`: `#059669` (Success, Savings)
  - `warm-amber`: `#F5A623` (Accents, LATAM signal)
  - `slate`: `#0F172A` (Primary Text)
- **Typography:**
  - Headlines: `Plus Jakarta Sans 700`
  - Body/UI: `Inter 400`
  - Savings/Figures: `Inter 700`
- **Radius:** `0.5rem` (shadcn default)
- **Breakpoints:** Mobile (390px), Tablet (768px), Desktop (1440px).

## 5. Component Library Conventions (shadcn/ui)
- Buttons: `Primary` (Deep Teal), `Outline` (Slate), `Ghost`.
- Cards: Standard shadcn `Card` with `surface` background.
- Status Chips: Mapped to backend keys.
- Navigation: Left sidebar (Desktop), Bottom Tabs (Mobile).

## 6. Localization & Content Guidelines
- **Single-language UI:** Instant toggle between EN and ES.
- **Microcopy:** Use plain language. "Fraud Score" over "Risk Assessment Matrix."
- **Bilingual Terms:** Dual-language labels only for critical financial terms.

## 7. Status Mapping Table
| Backend Key | UI Label (ES/EN) | Color Token | Style |
| :--- | :--- | :--- | :--- |
| `uploaded` | Subido / Uploaded | `muted-gray` | Solid Pill |
| `processing` | Procesando / Processing | `dark-navy` | Pulsing Pill |
| `extracted` | Extraído / Extracted | `deep-teal` | Solid Pill |
| `analyzed` | Analizado / Analyzed | `deep-teal` | Solid Pill |
| `compliance_checked` | Cumplimiento ✓ / Compliance ✓ | `emerald` | Solid Pill |
| `routed` | Enrutado ✓ / Routed ✓ | `emerald` | Solid Pill |
| `failed` | Error / Failed | `danger-red` | Solid Pill |

## 8. Accessibility Checklist (WCAG AA)
- Minimum contrast ratio 4.5:1 for text.
- Interactive elements min 44x44px on mobile.
- Clear focus states for keyboard navigation.
- Aria-labels for all icons and status changes.

## 9. Responsive Rules
- **Desktop:** Full sidebar (240px) + Main content.
- **Tablet:** Icon-only sidebar + single column layouts.
- **Mobile:** Bottom Tab Bar + Floating Action Button (FAB) for Upload.

## 10. Motion & Interaction Guidelines
- **Processing state:** Subtle pulse animation on pipeline nodes.
- **Hover states:** Card lifts (2px), Button opacity shifts.
- **Transitions:** Smooth fade (200ms) between workflow steps.

## 11. Trust & Compliance Messaging
- Footer: "Powered by Google Cloud AI."
- Security note: "🔒 Cifrado de extremo a extremo."
- Service note: "Verificación de corredor incluida en el análisis."

## 12. Empty States
- Large centered icons with clear CTAs (e.g., "Your first invoice is 15 seconds away").

## 13. Coming Soon Roadmap (V2–V5)
- Displayed as grayed-out/locked items in the sidebar or a dedicated "Roadmap" section in Settings.
- Labels: "Coming Soon" / "Próximamente."

## 14. Handoff Notes
- **Tech Stack:** Next.js 14, TailwindCSS, shadcn/ui, Vercel.
- Use `next-intl` or similar for instant i18n switching.
- Tailwind config must include the exact hex codes provided in Design Tokens.
