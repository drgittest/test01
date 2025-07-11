# API Documentation

## Overview
This document describes the API endpoints for the Order Management System, including the new modal functionality that replaces the order detail page.

## Base URL
```
http://localhost:8000
```

## Authentication
Most endpoints require authentication via session cookies. Users must be logged in to access protected endpoints.

## Endpoints

### 1. User Management

#### 1.1 User Registration
- **URL**: `/register`
- **Method**: `GET`, `POST`
- **Description**: User registration page and form processing
- **GET Response**: HTML registration form
- **POST Data**:
  ```json
  {
    "login_id": "string",
    "password": "string"
  }
  ```
- **Success Response**: Redirect to `/login` (302)
- **Error Response**: HTML with error message

#### 1.2 User Login
- **URL**: `/login`
- **Method**: `GET`, `POST`
- **Description**: User authentication
- **GET Response**: HTML login form
- **POST Data**:
  ```json
  {
    "login_id": "string",
    "password": "string"
  }
  ```
- **Success Response**: Redirect to `/` with session token (302)
- **Error Response**: HTML with error message

#### 1.3 User Logout
- **URL**: `/logout`
- **Method**: `GET`
- **Description**: Clear user session
- **Response**: Redirect to `/login` (302)

### 2. Order Management

#### 2.1 List Orders
- **URL**: `/orders`
- **Method**: `GET`
- **Description**: Display all orders in a table format
- **Authentication**: Required
- **Response**: HTML page with orders table and modal functionality
- **Features**:
  - Responsive table layout
  - Alpine.js modal integration
  - Tailwind CSS styling
  - Click-to-view order details

#### 2.2 Create Order
- **URL**: `/orders/create`
- **Method**: `GET`, `POST`
- **Description**: Create new order form and processing
- **Authentication**: Required
- **GET Response**: HTML creation form
- **POST Data**:
  ```json
  {
    "order_number": "string",
    "customer_name": "string",
    "item": "string",
    "quantity": "integer",
    "price": "integer",
    "status": "string" // optional, defaults to "pending"
  }
  ```
- **Success Response**: Redirect to `/orders` (302)
- **Error Response**: HTML with error message

#### 2.3 Edit Order
- **URL**: `/orders/{order_id}/edit`
- **Method**: `GET`, `POST`
- **Description**: Edit existing order
- **Authentication**: Required
- **Parameters**:
  - `order_id` (path): Order ID to edit
- **GET Response**: HTML edit form with pre-filled data
- **POST Data**:
  ```json
  {
    "order_number": "string",
    "customer_name": "string",
    "item": "string",
    "quantity": "integer",
    "price": "integer",
    "status": "string"
  }
  ```
- **Success Response**: Redirect to `/orders` (302)
- **Error Response**: HTML with error message or 404 if order not found

### 3. API Endpoints

#### 3.1 Get Order Details (JSON API)
- **URL**: `/api/orders/{order_id}`
- **Method**: `GET`
- **Description**: Get order details as JSON for modal display
- **Authentication**: Required
- **Parameters**:
  - `order_id` (path): Order ID to retrieve
- **Success Response** (200):
  ```json
  {
    "id": 1,
    "order_number": "ORD-001",
    "customer_name": "John Doe",
    "item": "Product Name",
    "quantity": 5,
    "price": 1000,
    "status": "pending",
    "created_at": "2024-01-01T10:00:00",
    "updated_at": "2024-01-01T10:00:00"
  }
  ```
- **Error Responses**:
  - `400 Bad Request`: Invalid order ID format
    ```json
    {
      "error": "Invalid order ID format",
      "details": "Order ID must be a positive integer"
    }
    ```
  - `404 Not Found`: Order not found
    ```json
    {
      "error": "Order not found",
      "order_id": 999
    }
    ```
  - `500 Internal Server Error`: Unexpected error
    ```json
    {
      "error": "Internal server error",
      "details": "An unexpected error occurred"
    }
    ```

## Frontend Integration

### Alpine.js Component
The orders list page uses Alpine.js for modal functionality:

```javascript
function orderModal() {
    return {
        isOpen: false,
        loading: false,
        orderData: null,
        
        openModal(orderId) {
            // Opens modal and fetches order data
        },
        
        closeModal() {
            // Closes modal and resets state
        },
        
        formatDate(dateString) {
            // Formats date for display
        },
        
        formatCurrency(amount) {
            // Formats currency values
        },
        
        getStatusClasses(status) {
            // Returns CSS classes for status badges
        }
    }
}
```

### Modal API Usage
```javascript
// Example of fetching order data
fetch(`/api/orders/${orderId}`)
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: Order not found`);
        }
        return response.json();
    })
    .then(data => {
        // Update modal content with order data
        this.orderData = data;
        this.loading = false;
    })
    .catch(error => {
        console.error('Error loading order details:', error);
        this.loading = false;
    });
```

## Error Handling

### HTTP Status Codes
- `200 OK`: Successful request
- `302 Found`: Redirect response
- `400 Bad Request`: Invalid request data
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

### Error Response Format
All JSON error responses follow this format:
```json
{
    "error": "Error message",
    "details": "Additional details if available"
}
```

## Data Models

### Order Model
```python
class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String, index=True)
    customer_name = Column(String)
    item = Column(String)
    quantity = Column(Integer)
    price = Column(Integer)
    status = Column(String, default="pending")
    created_at = Column(String)
    updated_at = Column(String)
```

### User Model
```python
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    login_id = Column(String, unique=True, index=True)
    password = Column(String)
```

## Security Considerations

### Authentication
- Session-based authentication using JWT tokens
- Protected routes require valid session
- Automatic redirect to login for unauthenticated requests

### Input Validation
- Order ID validation (must be positive integer)
- Form data validation on server side
- SQL injection protection via SQLAlchemy ORM

### Error Handling
- Generic error messages for security
- Proper HTTP status codes
- Input sanitization

## Rate Limiting
Currently no rate limiting implemented. Consider implementing for production use.

## CORS
CORS is not configured as this is a single-domain application. Configure CORS if needed for cross-origin requests.

## Testing

### Manual Testing
1. Start the server: `uvicorn main:app --reload --port 8000`
2. Navigate to `/login` and authenticate
3. Test order list page: `/orders`
4. Test modal functionality by clicking "View Details"
5. Test API endpoint directly: `/api/orders/1`

### Automated Testing
```bash
# Run visual tests
cd tests/visual
python simple_visual_test.py

# Run comprehensive tests
python test_modal_design.py
```

## Migration from Detail Page to Modal

### Changes Made
1. **Removed**: `/orders/{order_id}` route (order detail page)
2. **Added**: `/api/orders/{order_id}` route (JSON API endpoint)
3. **Updated**: `templates/orders.html` with Alpine.js modal
4. **Deleted**: `templates/order_detail.html`

### Benefits
- Improved user experience (no page navigation)
- Faster loading (AJAX requests)
- Better responsive design
- Reduced server load
- Consistent UI/UX

## Future Enhancements

### Potential Improvements
1. **Real-time Updates**: WebSocket integration for live order updates
2. **Bulk Operations**: API endpoints for bulk order operations
3. **Search and Filter**: API endpoints with query parameters
4. **Pagination**: API pagination for large order lists
5. **Export**: API endpoints for data export (CSV, JSON)
6. **Webhooks**: Notifications for order status changes

### API Versioning
Consider implementing API versioning for future changes:
```
/api/v1/orders/{order_id}
/api/v2/orders/{order_id}
```

## Support

For API-related issues:
1. Check server logs for error details
2. Verify authentication status
3. Test endpoints manually
4. Review this documentation
5. Check visual test results 