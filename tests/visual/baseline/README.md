# Baseline Screenshots for Visual Testing

This directory contains baseline screenshots used for automated visual testing of the order modal functionality.

## Screenshots

### Desktop (1920x1080)
- `expected_orders_list.png` - Orders list page in normal state
- `expected_modal_open.png` - Mock modal window in open state with order details

### Mobile (375x667 - iPhone SE)
- `expected_orders_list_mobile.png` - Orders list page on mobile viewport
- `expected_modal_open_mobile.png` - Mock modal window on mobile viewport

## Expected Visual State

### Orders List Page
- Clean table layout with order data
- Responsive design that adapts to screen size
- Proper spacing and typography
- No modal visible initially

### Modal Window
- Centered modal with backdrop
- Order details displayed in structured format
- Close button (X) in top-right corner
- Edit button for navigation to edit page
- Proper focus management and keyboard navigation

## Usage

These baseline screenshots are used by the automated visual testing suite to:
1. Compare current visual state against expected state
2. Detect visual regressions
3. Ensure consistent appearance across different environments
4. Validate responsive design behavior

## Screenshot Types

### Real Screenshots
- `expected_orders_list.png` - Actual screenshot of orders list page
- `expected_orders_list_mobile.png` - Actual screenshot of orders list on mobile

### Mock Screenshots
- `expected_modal_open.png` - Mock modal for testing (created manually)
- `expected_modal_open_mobile.png` - Mock mobile modal for testing

## Regenerating Baselines

To regenerate these baseline screenshots:

```bash
cd tests/visual
python create_baseline_screenshots_simple.py  # For real screenshots
python create_manual_baseline.py              # For mock screenshots
```

## Notes

- Real screenshots are taken in headless Chrome with consistent settings
- Mock screenshots are created programmatically for testing purposes
- Window size is fixed at 1920x1080 for desktop and 375x667 for mobile
- JavaScript is enabled for proper modal functionality
- Screenshots include the full page content for comprehensive comparison
