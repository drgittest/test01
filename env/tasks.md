# Issue 1: Add Unit Tests for Routes That Are Missing in the Current Test

## Task Breakdown

1. **Audit Existing Tests**
   - [x] Review `test_main.py` and any other test files to list which routes are already covered.

### Existing Test Coverage (from test_main.py):
- `/register` (GET, POST)
- `/login` (GET, POST: success and failure)

**Not covered:**
- `/logout`
- `/` (index)
- `/orders` (GET)
- `/orders/create` (GET, POST)
- `/orders/{order_id}` (GET)
- `/orders/{order_id}/edit` (GET, POST)

2. **List All Application Routes**
   - [x] Review `main.py` (and any routers) to enumerate all available API and page routes.

### All Application Routes (from main.py):
- `/` (index)
- `/register` (GET, POST)
- `/login` (GET, POST)
- `/logout`
- `/orders` (GET)
- `/orders/` (GET)
- `/orders/create` (GET, POST)
- `/orders/{order_id}` (GET)
- `/orders/{order_id}/edit` (GET, POST)

3. **Identify Missing Test Coverage**
   - [x] Compare the list of all routes with the list of tested routes.
   - [x] Create a checklist of routes that do not have corresponding tests.

### Routes Missing Test Coverage:
- `/logout`
- `/` (index)
- `/orders` (GET)
- `/orders/create` (GET, POST)
- `/orders/{order_id}` (GET)
- `/orders/{order_id}/edit` (GET, POST)

4. **Write Unit Tests for Each Missing Route**
   - [x] For each missing route:
     - [x] Write a test for successful (expected) behavior.
     - [x] Write tests for common failure or edge cases (e.g., invalid input, unauthorized access).

5. **Refactor and Organize Tests**
   - [x] Ensure tests are organized and named clearly.
   - [x] Use fixtures for setup/teardown if needed.

6. **Run and Validate Tests**
   - [x] Run `pytest` to ensure all new tests pass and existing tests are not broken.
   - [x] Fix any issues or errors found during testing.

7. **Update Documentation**
   - [ ] Update `README.md` or other docs to reflect improved test coverage if necessary.

---

*Use this checklist to track progress as you add comprehensive unit tests for all routes in your application.* 

---

## Test Coverage & How to Run

All main application and order-related routes are now covered by unit tests, including registration, login, logout, order creation, listing, detail, and editing (GET and POST). Tests also cover both successful and failure/edge cases where appropriate.

To run the tests, activate your virtual environment and run:

    pytest -v

All tests should pass. See warnings for possible future deprecations (e.g., Pydantic/Starlette changes). 