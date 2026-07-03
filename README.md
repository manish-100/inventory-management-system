# Inventary Order System

Assessment-ready project for managing products, customers, orders and inventary tracking.

## Tech Stack

- Backend: Python, FastAPI, SQLAlchemy, Alembic
- Frontend: React + Vite
- Database: PostgreSQL
- Containerization: Docker + Docker Compose

## Features Covered

- Product CRUD
- Customer CRUD
- Order creation
- Inventary tracking
- Unique product SKU validation
- Unique customer email validation
- Automatic stock reduction when orders are placed
- Prevent order creation when stock is insufficient
- Product/customer delete protection when records are used in orders
- Order delete restores stock
- Environment variables
- Dockerized backend, frontend and PostgreSQL
- Swagger API documentation

## Run with Docker Compose

```bash
cd Inventary-Order-System
docker compose up --build
```

Open:

```text
Frontend: http://localhost:5173
Backend API: http://localhost:8000
Swagger Docs: http://localhost:8000/docs
Health Check: http://localhost:8000/health
```

## Run without Docker

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
copy .env.example .env
npm install
npm run dev
```

## Test Flow

1. Create a product with SKU `P001`, price `100`, stock `10`.
2. Try creating another product with SKU `P001`; API should reject it.
3. Create a customer with email `test@example.com`.
4. Try creating another customer with same email; API should reject it.
5. Place order for product quantity `2`; stock should reduce from `10` to `8`.
6. Place order with quantity higher than stock; API should reject it.
7. Try deleting product/customer used in order; API should reject it.
8. Delete order; stock should be restored.

## Render Backend Deployment

1. Push project to GitHub.
2. Create PostgreSQL database on Render.
3. Create a Web Service.
4. Root directory: `backend`
5. Build command:

```bash
pip install -r requirements.txt
```

6. Start command:

```bash
alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

7. Add environment variables:

```text
DATABASE_URL=<Render PostgreSQL Internal Database URL>
FRONTEND_ORIGIN=<Vercel frontend URL>
```

## Vercel Frontend Deployment

1. Import GitHub repository in Vercel.
2. Root directory: `frontend`
3. Add environment variable:

```text
VITE_API_BASE_URL=<Render backend URL>/api
```

4. Deploy.

## Docker Hub Backend Image

```bash
cd backend
docker build -t your-dockerhub-username/inventory-api:latest .
docker login
docker push your-dockerhub-username/inventory-api:latest
```

Docker Hub image link format:

```text
https://hub.docker.com/r/your-dockerhub-username/inventory-api
```
