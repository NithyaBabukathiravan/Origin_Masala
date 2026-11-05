# ORIGIN Admin + Customer Store Updates

## Changes included
- Admin Products list now uses product-name image matching against the customer frontend's `frontend/public/images` assets when a product has a local/missing image, and shows a safe fallback image if an image fails.
- Product form supports a direct image URL (including RustFS URLs) and a dropdown to choose any existing customer frontend image.
- Product list has client-side pagination (5/10/20/50 rows per page) and resets to page 1 when search/category/page size changes.
- Admin Categories list now displays category thumbnails using the customer frontend images (`w1.jpeg`, `s2.jpeg`, `t3.jpeg`, `co1.jpeg`).
- Admin coupon defaults now include `SAVE30`, `SAVE50`, `SAVE60`, `SAVE100` with matching fixed discounts/minimum cart values.
- Customer checkout now also accepts `SAVE60` (₹60 off orders of ₹600+).
- Backend product/category primary keys already use UUIDs in this project; admin API passes the UUID product/category IDs through without converting them to numeric IDs.

## Run
1. Extract this ZIP.
2. Backend: open a terminal in `masal/backend`, activate your existing virtual environment, then run `uvicorn app.main:app --reload`.
3. Frontend: open a terminal in `masal/frontend`, run `npm install`, then `npm run dev`.
4. Open the customer site and `/admin`. Log in using your configured admin credentials.

## Image notes
- The dropdown selects an existing image served by the customer frontend, e.g. `/images/w1.jpeg`. These paths work on the same frontend origin.
- For images shared across other computers/deployments, use a publicly reachable RustFS object URL in the Image URL field. A `localhost` URL only works on your own machine.
- This update does not add a new backend binary-upload endpoint. The “Choose image” dropdown selects existing frontend assets; use the URL field for RustFS-hosted images.
- Admin coupon page is currently local frontend state (as in the original project), not database-backed. Its preset codes match the customer checkout, but edits made in admin do not automatically update the checkout/backend coupon rules. The checkout coupon rules are hard-coded in `frontend/src/components/Checkout.jsx`.
