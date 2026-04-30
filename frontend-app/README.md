# Puente AI — Frontend

Frontend for **Puente AI**, a cross-border trade intelligence and payment routing platform for Miami ↔ LATAM SME importers. Upload an invoice, get a fraud score, compliance signals, and the cheapest routing recommendation.

## Stack

- Vite + React 18 + TypeScript
- Tailwind CSS + shadcn/ui
- Firebase Auth (email/password, Google, Apple)
- React Router

## Run locally

```bash
npm install
npm run dev
```

The app starts on `http://localhost:8080` (or the next free port).

## Environment variables

Create a `.env.local` in the project root:

```
VITE_API_URL=https://puente-backend-519686233522.us-central1.run.app/api/v1
```

| Variable        | Purpose                                                                 | Default                                                                           |
| --------------- | ----------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| `VITE_API_URL`  | Base URL of the Puente FastAPI backend (Cloud Run). Used for `/upload`, `/analyze`, `/compliance`, `/routing`. | `https://puente-backend-519686233522.us-central1.run.app/api/v1` |

All authenticated calls attach a Firebase ID token as `Authorization: Bearer <jwt>`.

## Scripts

- `npm run dev` — start the dev server
- `npm run build` — production build
- `npm run preview` — preview the production build
- `npm run test` — run Vitest tests
