# ORIGIN project updates

This archive preserves the original `frontend` and `backend` source and adds the requested admin features.

## Admin features
- Recipes page: the six existing recipes are seeded once on backend startup; admin can add, edit, and delete recipes including description, category, cooking time, ingredients, instructions, and image URL/upload.
- Recipe Categories page: create, edit, and delete recipe categories with name, description, image URL, and image upload. A category cannot be deleted while recipes still use it.
- Homepage slideshow: Settings accepts multiple image URLs and image uploads. Save settings to apply them to the storefront in the same browser/origin.
- Coupons page: coupons are loaded from the backend and can be created, edited, and deleted. Configure discount type/value, minimum order, usage limit, expiry, and required completed orders.
- Pagination: Products (existing), Categories, Orders, Customers, Coupons, Recipes, and Recipe Categories.
- Removed the eye/view action from the Dashboard recent-orders table.

## Coupon security
- Checkout loads active coupons from the backend.
- Applying a coupon requires a valid 10-digit phone number and checks the backend for completed-order requirements and prior redemption.
- The order endpoint validates the coupon again at order placement, calculates the discount on the server, records the phone/coupon redemption, and increments coupon usage.
- A unique database constraint on `(phone, coupon_id)` prevents the same phone from redeeming the same coupon twice, including refreshes or other devices.

## Start locally
1. Open a terminal in `backend` and activate your existing virtual environment (or create one).
2. Install backend dependencies: `pip install -r requirements.txt`.
3. Ensure MySQL is running and `backend/.env` has the correct local database settings.
4. Run: `uvicorn app.main:app --reload` (API docs: `http://127.0.0.1:8000/docs`).
5. Open another terminal in `frontend`, run `npm install`, then `npm run dev`.

The backend creates the new recipe tables on startup and adds the `required_orders` coupon column to an existing coupons table. Back up your database before first run.

## Verification note
Python source syntax and frontend JSX parsing were checked. A full Vite production build could not be completed in this environment because the uploaded `node_modules` was missing its platform-specific Rolldown native binding; run `npm install` in `frontend` on your Windows machine before `npm run build`.
