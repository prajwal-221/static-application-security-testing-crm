# IDURAR ERP/CRM

**IDURAR ERP/CRM** is a modern, full-stack **Enterprise Resource Planning (ERP)** and **Customer Relationship Management (CRM)** system designed to help businesses manage finance, customers, inventory, users, and reporting from a single, unified platform.

Built with a **React + Node.js + MongoDB** (**MERN)** stack and fully containerized using  **Docker Compose** , IDURAR focuses on scalability, maintainability, and developer experience.

---

## Key Capabilities

* End-to-end **business management**
* Modular and extensible architecture
* REST-based backend API
* Secure authentication and role-based access
* Production-ready Docker setup

---

## Screenshot

![1768458966325](image/README/1768458966325.png)

![1768459058601](image/README/1768459058601.png)

![1768388299790](image/README/1768388299790.png)

![1768388324141](image/README/1768388324141.png)

![1768388350636](image/README/1768388350636.png)

![1768388377021](image/README/1768388377021.png)

## **Application Features**

### Dashboard Overview

* Real-time business snapshot
* Monthly summaries for:
  * Invoices
  * Quotes
  * Paid & Unpaid amounts
* Visual status indicators and progress tracking
* Customer growth and activity insights

---

### Customer Management

* Centralized customer database
* Track active customers
* Monitor new customers added each month
* View customer-related invoices and quotes
* Designed for fast lookup and relationship tracking

---

### Invoice Management

* Create and manage invoices with ease
* Invoice lifecycle tracking
* Monthly invoice analytics
* Clear separation between paid and outstanding invoices

---

### Quote Management

* Generate professional quotes for customers
* Quote status tracking
* Seamless transition from quote to invoice
* Monthly quote summaries

---

### Payments

* Record and track payments
* Associate payments with invoices
* Support for partial payments
* Clear visibility into payment history

---

### Payment Modes

* Configure multiple payment methods
* Flexible setup for different business needs
* Easy extension for future gateways

---

### Taxes

* Tax configuration and management
* Apply taxes to invoices and quotes
* Designed for multi-tax and regional expansion

---

### Settings

* Application-level configuration
* Business and financial preferences
* Scalable for enterprise-grade customization

## Tech Stack

### Frontend

| Technology       | Version | Purpose          |
| ---------------- | ------- | ---------------- |
| React            | 18.3.1  | UI Library       |
| Redux Toolkit    | 2.2.1   | State Management |
| Ant Design       | 5.14.1  | UI Components    |
| Vite             | 5.4.8   | Build Tool       |
| React Router DOM | 6.22.0  | Routing          |
| Axios            | 1.6.2   | HTTP Client      |
| dayjs            | ^1.11.x | Date Handling    |
| react-quill      | ^2.x    | Rich Text Editor |

---

### Backend

| Technology | Version | Purpose            |
| ---------- | ------- | ------------------ |
| Node.js    | 20.9.0  | Runtime            |
| Express.js | 4.18.2  | REST API Framework |
| MongoDB    | 6.0     | Database           |
| Mongoose   | 8.1.1   | ODM                |
| JWT        | 9.0.2   | Authentication     |
| Multer     | 1.4.4   | File Uploads       |
| OpenAI SDK | 4.27.0  | AI Services        |
| Resend     | 2.0.0   | Email Delivery     |

---

### DevOps & Tooling

* Docker
* Docker Compose
* Git & GitHub
* Environment-based configuration
* ESLint & Prettier

---

## Project Structure

```
.
├── backend/        # Express API & business logic
├── frontend/       # React application
├── mongodb/        # MongoDB initialization & volumes
├── doc/            # Documentation
├── features/       # Feature definitions
├── docker-compose.yml
├── README.md
└── LICENSE
```

---

## Docker Setup (Recommended)

### Prerequisites

* Docker
* Docker Compose

### Run the Application

```bash
docker-compose up -d --build
```

### Access Services

* Frontend: `http://localhost:3000`
* Backend API: `http://localhost:4000`
* MongoDB: `localhost:27017`

---

## Local Development (Without Docker)

### Backend

```bash
cd backend
npm install
npm run dev
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## Environment Variables

### Backend (`.env`)

```
DATABASE="mongodb://root:rootpassword@mongodb:27017/idurar?authSource=admin"
JWT_SECRET="your_private_jwt_secret_key"
NODE_ENV="development"
OPENSSL_CONF='/dev/null'
PUBLIC_SERVER_FILE="http://localhost:4000/"
PORT=4000
```

---

## Security Highlights

* JWT-based authentication
* Secure password hashing
* Input validation
* CORS protection

---

## Database Collections

* users
* roles
* customers
* leads
* invoices
* payments
* products
* inventory
* expenses

---

## Architecture Overview

```
Browser
   ↓
Frontend (React + Vite)
   ↓
Backend API (Express)
   ↓
MongoDB (Docker)
```
