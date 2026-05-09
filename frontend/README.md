# Frontend (Next.js + React 19 + Tailwind)

## Stack
- Next.js App Router
- React 19.2.6
- Tailwind CSS

## Setup
1. Copy env:
   - `cp .env.example .env.local` (or on Windows: `Copy-Item .env.example .env.local`)
2. Install deps:
   - `npm install`
3. Run dev server:
   - `npm run dev`

Default app URL: `http://127.0.0.1:3000`

## Backend Integration
Set `NEXT_PUBLIC_API_BASE_URL` to your FastAPI server (default in `.env.example`):
- `http://127.0.0.1:8000`

## Main Routes
- `/` Home landing
- `/dashboard` Dashboard
- `/login` Login
- `/register` Register
- `/products` Product catalog
- `/products/[id]` Product detail
- `/cart` Local shopping cart
- `/checkout` Checkout from locally selected variants
- `/transactions` Logged-in user transaction list
- `/catalog` Compatibility redirect to `/products`

## Structure
This app follows a `src/`-first layout:

```text
frontend/
  src/
    app/
    components/
      ui/
      layout/
      features/
    features/
      auth/
      orders/
    lib/
    hooks/
    services/
    store/
    types/
    constants/
```

## Notes
- Auth token is stored in `localStorage` and mirrored into `auth_token` cookie.
- Catalog page uses server rendering with the auth cookie.
- Checkout uses FastAPI `/checkout` endpoint and sends `Idempotency-Key`.
- Transactions page reads `/checkout/transactions` for current user data.
