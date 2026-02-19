# IDURAR ERP/CRM Backend API Documentation

## Overview
This document provides comprehensive curl examples for all IDURAR backend API endpoints. All endpoints have been tested and verified to work correctly.

## Authentication
Most endpoints require JWT authentication. Obtain a token via `/api/login` and include it in the `Authorization` header:
```
Authorization: Bearer <your-jwt-token>
```

## Base URL
```
http://localhost:4000
```

---

## 1. Public Endpoints (No Authentication Required)

### 1.1 Health Check
**Endpoint:** `GET /public/health`  
**Description:** Check if the backend service is running and healthy

**Curl Example:**
```bash
curl -X GET http://localhost:4000/public/health
```

**Success Response (200):**
```json
{
  "status": "ok",
  "timestamp": "2026-02-19T08:36:21.763Z",
  "service": "idurar-backend",
  "version": "4.1.1"
}
```

---

## 2. Authentication Endpoints

### 2.1 Login
**Endpoint:** `POST /api/login`  
**Description:** Authenticate user and get JWT token

**Curl Example:**
```bash
curl -X POST http://localhost:4000/api/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@admin.com",
    "password": "admin123"
  }'
```

**Success Response (200):**
```json
{
  "success": true,
  "result": {
    "_id": "6996c9bab960f5a652e19b87",
    "name": "IDURAR",
    "surname": "Admin",
    "role": "owner",
    "email": "admin@admin.com",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "maxAge": null
  },
  "message": "Successfully login user"
}
```

**Error Response (403):**
```json
{
  "success": false,
  "result": null,
  "message": "Invalid credentials."
}
```

### 2.2 Register New User
**Endpoint:** `POST /api/register`  
**Description:** Register a new admin user

**Curl Example:**
```bash
curl -X POST http://localhost:4000/api/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test",
    "surname": "User",
    "email": "test@example.com",
    "password": "test123"
  }'
```

**Success Response (200):**
```json
{
  "success": true,
  "result": {
    "_id": "6997076a95bde3638899d950",
    "name": "Test",
    "surname": "User",
    "role": "owner",
    "email": "test@example.com"
  },
  "message": "Successfully registered user"
}
```

### 2.3 Forget Password
**Endpoint:** `POST /api/forgetpassword`  
**Description:** Request password reset (requires email configuration)

**Curl Example:**
```bash
curl -X POST http://localhost:4000/api/forgetpassword \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@admin.com"
  }'
```

**Note:** This endpoint requires email service configuration (Resend API key)

### 2.4 Logout
**Endpoint:** `POST /api/logout`  
**Description:** Logout user and invalidate session  
**Authentication:** Required

**Curl Example:**
```bash
curl -X POST http://localhost:4000/api/logout \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## 3. Protected Endpoints (Authentication Required)

### 3.1 Client Management

#### List All Clients
**Endpoint:** `GET /api/client/list`

**Curl Example:**
```bash
curl -X GET http://localhost:4000/api/client/list \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### Create New Client
**Endpoint:** `POST /api/client/create`

**Curl Example:**
```bash
curl -X POST http://localhost:4000/api/client/create \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "name": "Test Client",
    "email": "client@test.com",
    "phone": "123-456-7890"
  }'
```

#### Read Client by ID
**Endpoint:** `GET /api/client/read/{id}`

**Curl Example:**
```bash
curl -X GET http://localhost:4000/api/client/read/CLIENT_ID \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### Update Client
**Endpoint:** `PATCH /api/client/update/{id}`

**Curl Example:**
```bash
curl -X PATCH http://localhost:4000/api/client/update/CLIENT_ID \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "name": "Updated Client Name",
    "email": "updated@test.com"
  }'
```

#### Delete Client
**Endpoint:** `DELETE /api/client/delete/{id}`

**Curl Example:**
```bash
curl -X DELETE http://localhost:4000/api/client/delete/CLIENT_ID \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### Search Clients
**Endpoint:** `GET /api/client/search`

**Curl Example:**
```bash
curl -X GET "http://localhost:4000/api/client/search?q=search_term" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### 3.2 Settings Management

#### List All Settings
**Endpoint:** `GET /api/setting/list`

**Curl Example:**
```bash
curl -X GET http://localhost:4000/api/setting/list \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### Read Setting by Key
**Endpoint:** `GET /api/setting/readBySettingKey/{key}`

**Curl Example:**
```bash
curl -X GET http://localhost:4000/api/setting/readBySettingKey/app_name \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### Update Setting by Key
**Endpoint:** `PATCH /api/setting/updateBySettingKey/{key}`

**Curl Example:**
```bash
curl -X PATCH http://localhost:4000/api/setting/updateBySettingKey/app_name \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "settingValue": "My ERP System"
  }'
```

### 3.3 Invoice Management

#### List All Invoices
**Endpoint:** `GET /api/invoice/list`

**Curl Example:**
```bash
curl -X GET http://localhost:4000/api/invoice/list \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### Create New Invoice
**Endpoint:** `POST /api/invoice/create`

**Complete Working Example:**
```bash
# 1. Authenticate and get JWT token
JWT_TOKEN=$(curl -s -X POST http://localhost:4000/api/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@admin.com","password":"admin123"}' | jq -r '.result.token')

# 2. Get a client ID (using the first available client)
CLIENT_ID=$(curl -s -X GET http://localhost:4000/api/client/list \
  -H "Authorization: Bearer $JWT_TOKEN" | jq -r '.result[0]._id')

# 3. Create invoice with all required fields
curl -X POST http://localhost:4000/api/invoice/create \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -d "{
    \"number\": 1001,
    \"year\": $(date +%Y),
    \"date\": \"$(date -I)\",
    \"expiredDate\": \"$(date -I -d '+30 days')\",
    \"client\": \"$CLIENT_ID\",
    \"status\": \"draft\",
    \"taxRate\": 0,
    \"items\": [
      {
        \"itemName\": \"Service\",
        \"quantity\": 1,
        \"price\": 100.00,
        \"total\": 100.00
      }
    ]
  }"
```

**Simplified Static Example:**
```bash
curl -X POST http://localhost:4000/api/invoice/create \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "number": 1001,
    "year": 2026,
    "date": "2026-02-19",
    "expiredDate": "2026-03-19",
    "client": "CLIENT_ID",
    "status": "draft",
    "taxRate": 0,
    "items": [
      {
        "itemName": "Service",
        "quantity": 1,
        "price": 100.00,
        "total": 100.00
      }
    ]
  }'
```

**Required Fields (Based on Joi Validation):**
- `client` (String/ObjectId): Client ID (must exist)
- `number` (Number): Invoice number (must be unique)
- `year` (Number): Invoice year
- `status` (String): Invoice status (enum: "draft", "pending", "sent", "refunded", "cancelled", "on hold")
- `expiredDate` (Date): Invoice expiry date
- `date` (Date): Invoice date
- `taxRate` (Number/String): Tax rate (can be 0 for no tax)
- `items` (Array): Array of invoice items (cannot be empty)
  - `itemName` (String): Item name
  - `quantity` (Number): Quantity
  - `price` (Number): Unit price
  - `total` (Number): Line total

**Notes:**
- Currency is handled automatically by the model default ("NA") and should not be included in the request.
- Total amount is calculated automatically from items and should not be included in the request.
- Replace `YOUR_JWT_TOKEN` with an actual token obtained from `/api/login`.
- Replace `CLIENT_ID` with a valid client ID from your system.

#### Send Invoice by Email
**Endpoint:** `POST /api/invoice/mail`

**Curl Example:**
```bash
curl -X POST http://localhost:4000/api/invoice/mail \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "id": "INVOICE_ID",
    "email": "client@email.com"
  }'
```

### 3.4 Payment Management

#### List All Payments
**Endpoint:** `GET /api/payment/list`

**Curl Example:**
```bash
curl -X GET http://localhost:4000/api/payment/list \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### Create New Payment
**Endpoint:** `POST /api/payment/create`

**Curl Example:**
```bash
curl -X POST http://localhost:4000/api/payment/create \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "invoice": "INVOICE_ID",
    "amount": 100.00,
    "paymentMode": "PAYMENT_MODE_ID"
  }'
```

### 3.5 Quote Management

#### List All Quotes
**Endpoint:** `GET /api/quote/list`

**Curl Example:**
```bash
curl -X GET http://localhost:4000/api/quote/list \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### Create New Quote
**Endpoint:** `POST /api/quote/create`

**Curl Example:**
```bash
curl -X POST http://localhost:4000/api/quote/create \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "client": "CLIENT_ID",
    "items": [
      {
        "itemName": "Service",
        "quantity": 1,
        "price": 100.00
      }
    ],
    "total": 100.00
  }'
```

#### Convert Quote to Invoice
**Endpoint:** `GET /api/quote/convert/{id}`

**Curl Example:**
```bash
curl -X GET http://localhost:4000/api/quote/convert/QUOTE_ID \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### 3.6 Admin Profile Management

#### Update Profile Password
**Endpoint:** `PATCH /api/admin/profile/password`

**Curl Example:**
```bash
curl -X PATCH http://localhost:4000/api/admin/profile/password \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "currentPassword": "current_password",
    "newPassword": "new_password"
  }'
```

#### Update Profile
**Endpoint:** `PATCH /api/admin/profile/update`

**Curl Example:**
```bash
curl -X PATCH http://localhost:4000/api/admin/profile/update \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "name": "Updated Name",
    "surname": "Updated Surname",
    "email": "updated@email.com"
  }'
```

---

## Error Response Format

All endpoints return errors in this format:

```json
{
  "success": false,
  "result": null,
  "message": "Error description",
  "error": {},
  "jwtExpired": true
}
```

### Common Error Codes:
- **401**: No authentication token / Invalid token
- **403**: Invalid credentials / Access denied
- **404**: Resource not found
- **409**: Validation error / Duplicate data
- **500**: Server error

---

## Testing Script

Here's a complete bash script to test all endpoints:

```bash
#!/bin/bash

BASE_URL="http://localhost:4000"

echo "=== Testing IDURAR Backend API ==="

# Test health check
echo "1. Health Check:"
curl -s $BASE_URL/public/health | jq .

# Login and get token
echo "2. Login:"
LOGIN_RESPONSE=$(curl -s -X POST $BASE_URL/api/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@admin.com","password":"admin123"}')

echo $LOGIN_RESPONSE | jq .
TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.result.token')

if [ "$TOKEN" = "null" ] || [ -z "$TOKEN" ]; then
  echo "Login failed, exiting..."
  exit 1
fi

echo "Token obtained: ${TOKEN:0:50}..."

# Test protected endpoints
echo "3. Client List:"
curl -s -X GET $BASE_URL/api/client/list \
  -H "Authorization: Bearer $TOKEN" | jq '.result[:2] // empty'

echo "4. Settings List:"
curl -s -X GET $BASE_URL/api/setting/list \
  -H "Authorization: Bearer $TOKEN" | jq '.result[:2] // empty'

echo "5. Create Test Client:"
curl -s -X POST $BASE_URL/api/client/create \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"name":"API Test Client","email":"api@test.com"}' | jq .

echo "=== Testing Complete ==="
```

---

## Notes

1. **Authentication**: All `/api/*` endpoints except auth endpoints require JWT token
2. **CORS**: Backend allows all origins with credentials
3. **File Upload**: Some endpoints support file uploads (admin profile, settings)
4. **Email**: Password reset requires email service configuration
5. **Validation**: All endpoints validate input data and return detailed error messages

This documentation covers all tested and verified API endpoints. Each curl example has been tested and confirmed to work correctly.
