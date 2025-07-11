# Order Feature Implementation Tasks

## 1. Database Model
- [ ] Create an `Order` model in `models.py` with fields such as:
    - `id` (primary key)
    - `order_number` (string, unique)
    - `customer_name` (string)
    - `item` (string)
    - `quantity` (integer)
    - `price` (float/decimal)
    - `status` (string or enum, e.g., pending/complete/cancelled)
    - `created_at` (datetime)
    - `updated_at` (datetime)
- [ ] Generate and apply a migration for the new table (if using Alembic).

## 2. Backend Endpoints
- [ ] Add endpoint to list all orders (GET `/orders`).
- [ ] Add endpoint to show order creation form (GET `/orders/create`).
- [ ] Add endpoint to handle order creation (POST `/orders/create`).
- [ ] Add endpoint to show order detail (GET `/orders/{order_id}`).
- [ ] Add endpoint to show order edit form (GET `/orders/{order_id}/edit`).
- [ ] Add endpoint to handle order update (POST `/orders/{order_id}/edit`).

## 3. Templates
- [ ] Create `orders.html` for listing all orders.
- [ ] Create `order_create.html` for the order creation form.
- [ ] Create `order_edit.html` for the order edit form.
- [ ] Create `order_detail.html` for displaying order details.

## 4. Frontend Integration
- [ ] Add navigation links to the order pages (e.g., in a navbar or sidebar).
- [ ] Ensure forms validate input and display errors as needed.

## 5. Testing
- [ ] Add unit tests for order creation, listing, detail, and editing endpoints.
- [ ] Add tests for form validation and error handling.

## 6. Documentation
- [ ] Update `README.md` with instructions for using the new order features.

---

**Optional Enhancements:**
- [ ] Add pagination to the order listing page.
- [ ] Add search/filter functionality to the order listing.
- [ ] Add authentication/authorization for order management.
- [ ] Add order deletion feature. 