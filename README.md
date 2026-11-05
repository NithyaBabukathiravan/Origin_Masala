# Masal Store — Unified Storefront and Admin

The customer storefront and admin dashboard now run from one React/Vite frontend. The FastAPI backend remains the shared API and database for products, categories, coupons, and orders.

## Project layout

- `frontend/` — customer storefront and `/admin` dashboard
- `backend/` — FastAPI API, SQLAlchemy models, database schema and admin seeding

The old `origin-admin` separate application is not needed in this merged project.

## 1. Configure the backend

Copy `backend/.env.example` to `backend/.env` and set your database URL, a long random JWT secret, and a strong admin password. Ensure the MySQL database exists before starting the API. Do not share `.env` or commit it to source control.

Windows PowerShell:

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python seed_admin.py
uvicorn app.main:app --reload
```

API docs: `http://127.0.0.1:8000/docs`

## 2. Run the unified frontend

Open a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open the URL printed by Vite, usually `http://localhost:5173`.

- Customer storefront: `/`
- Admin dashboard: `/admin`

If your API is not at `http://127.0.0.1:8000/api/v1`, create `frontend/.env` from `.env.example` and set `VITE_API_BASE_URL` accordingly.

## Included admin work

- Admin login through the shared backend token endpoint
- Product CRUD using the same products table the customer storefront reads
- Category CRUD using the shared categories table
- Customer directory derived from actual order records, not hard-coded sample customers
- Sales report derived from order records, with date-range selection and CSV export
- Store preferences page (currently browser-local preferences; it does not modify backend secrets)
- Notification UI and the separate notifications page removed
- Product/category/order identifiers use the backend UUID model where applicable

## Important behavior

Products and categories created in admin are saved through the shared API. Active products and categories are then fetched by the customer storefront. Orders submitted at checkout are posted to the backend and feed the admin customer and sales reports. Cancelled orders are excluded from net sales calculations.

For a clean start, ensure `backend/.env` has valid values and the MySQL database is running. The API must be running for shared product, category, order, and report data to work.
