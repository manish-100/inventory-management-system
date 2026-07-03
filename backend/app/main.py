from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.products import router as products_router
from app.api.customers import router as customers_router
from app.api.orders import router as orders_router
from app.api.dashboard import router as dashboard_router
from app.core.config import settings

app = FastAPI(title='Inventary Order System API', version='1.0.0')

allowed_origins = [
    settings.frontend_origin,
    'http://localhost:5173',
    'http://127.0.0.1:5173',
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

@app.get('/')
def root():
    return {'message': 'Inventary Order System API is running'}

@app.get('/health')
def health():
    return {'status': 'ok'}

app.include_router(products_router, prefix='/api')
app.include_router(customers_router, prefix='/api')
app.include_router(orders_router, prefix='/api')
app.include_router(dashboard_router, prefix='/api')
