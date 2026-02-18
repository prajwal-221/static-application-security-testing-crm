I'll analyze the backend routes for you. Let me examine the route files to understand the API structure.









Based on my analysis of the backend code, here are all the routes available in the CRM application:

## **Authentication Routes** (`/api`)
- `POST /api/login` - Admin login
- `POST /api/forgetpassword` - Forgot password
- `POST /api/resetpassword` - Reset password  
- `POST /api/register` - Register new admin
- `POST /api/logout` - Logout (requires auth token)

## **Core API Routes** (`/api`) - Requires Authentication
### Admin Management
- `GET /api/admin/read/:id` - Read admin by ID
- `PATCH /api/admin/password-update/:id` - Update admin password
- `PATCH /api/admin/profile/password` - Update profile password
- `PATCH /api/admin/profile/update` - Update admin profile (with photo upload)

### Settings Management
- `POST /api/setting/create` - Create setting
- `GET /api/setting/read/:id` - Read setting by ID
- `PATCH /api/setting/update/:id` - Update setting
- `GET /api/setting/search` - Search settings
- `GET /api/setting/list` - List settings (paginated)
- `GET /api/setting/listAll` - List all settings
- `GET /api/setting/filter` - Filter settings
- `GET /api/setting/readBySettingKey/:settingKey` - Read setting by key
- `GET /api/setting/listBySettingKey` - List settings by key
- `PATCH /api/setting/updateBySettingKey/:settingKey` - Update setting by key
- `PATCH /api/setting/upload/:settingKey` - Upload image for setting
- `PATCH /api/setting/updateManySetting` - Update multiple settings

## **Dynamic App Routes** (`/api`) - Requires Authentication
For each entity (client, invoice, payment, paymentMode, quote, taxes):
- `POST /api/{entity}/create` - Create new record
- `GET /api/{entity}/read/:id` - Read record by ID
- `PATCH /api/{entity}/update/:id` - Update record
- `DELETE /api/{entity}/delete/:id` - Delete record
- `GET /api/{entity}/search` - Search records
- `GET /api/{entity}/list` - List records (paginated)
- `GET /api/{entity}/listAll` - List all records
- `GET /api/{entity}/filter` - Filter records
- `GET /api/{entity}/summary` - Get summary statistics

### Special Routes for Invoice/Quote/Payment
- `POST /api/{entity}/mail` - Send via email (invoice, quote, payment)

### Special Routes for Quote
- `GET /api/quote/convert/:id` - Convert quote to invoice

## **Public Routes** (`/public`)
- `GET /public/health` - Health check endpoint
- `GET /public/:subPath/:directory/:file` - Serve static files

## **Download Routes** (`/download`)
- `GET /download/:directory/:file` - Download PDF files

## **Entities Available**
Based on the models found:
- `client` - Client management
- `invoice` - Invoice management  
- `payment` - Payment management
- `paymentMode` - Payment mode settings
- `quote` - Quote management
- `taxes` - Tax management

All API routes (except auth and public) require a valid authentication token passed in the request headers.
