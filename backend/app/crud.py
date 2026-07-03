from decimal import Decimal
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload
from app import models, schemas


def _commit(db: Session):
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail='Duplicate or invalid data')

# Product CRUD
def list_products(db: Session, search: str | None = None):
    query = db.query(models.Product)
    if search:
        term = f'%{search.strip()}%'
        query = query.filter(or_(models.Product.name.ilike(term), models.Product.sku.ilike(term)))
    return query.order_by(models.Product.id.desc()).all()

def get_product(db: Session, product_id: int):
    product = db.get(models.Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail='Product not found')
    return product

def create_product(db: Session, data: schemas.ProductCreate):
    if db.query(models.Product).filter(models.Product.sku == data.sku).first():
        raise HTTPException(status_code=400, detail='Product SKU already exists')
    product = models.Product(**data.model_dump())
    db.add(product)
    _commit(db)
    db.refresh(product)
    return product

def update_product(db: Session, product_id: int, data: schemas.ProductUpdate):
    product = get_product(db, product_id)
    if db.query(models.Product).filter(models.Product.sku == data.sku, models.Product.id != product_id).first():
        raise HTTPException(status_code=400, detail='Product SKU already exists')
    for key, value in data.model_dump().items():
        setattr(product, key, value)
    _commit(db)
    db.refresh(product)
    return product

def delete_product(db: Session, product_id: int):
    product = get_product(db, product_id)
    if db.query(models.OrderItem).filter(models.OrderItem.product_id == product_id).first():
        raise HTTPException(status_code=400, detail='Cannot delete product because it is used in orders')
    db.delete(product)
    _commit(db)
    return {'message': 'Product deleted successfully'}

# Customer CRUD
def list_customers(db: Session, search: str | None = None):
    query = db.query(models.Customer)
    if search:
        term = f'%{search.strip()}%'
        query = query.filter(or_(models.Customer.name.ilike(term), models.Customer.email.ilike(term)))
    return query.order_by(models.Customer.id.desc()).all()

def get_customer(db: Session, customer_id: int):
    customer = db.get(models.Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail='Customer not found')
    return customer

def create_customer(db: Session, data: schemas.CustomerCreate):
    if db.query(models.Customer).filter(models.Customer.email == data.email).first():
        raise HTTPException(status_code=400, detail='Customer email already exists')
    customer = models.Customer(**data.model_dump())
    db.add(customer)
    _commit(db)
    db.refresh(customer)
    return customer

def update_customer(db: Session, customer_id: int, data: schemas.CustomerUpdate):
    customer = get_customer(db, customer_id)
    if db.query(models.Customer).filter(models.Customer.email == data.email, models.Customer.id != customer_id).first():
        raise HTTPException(status_code=400, detail='Customer email already exists')
    for key, value in data.model_dump().items():
        setattr(customer, key, value)
    _commit(db)
    db.refresh(customer)
    return customer

def delete_customer(db: Session, customer_id: int):
    customer = get_customer(db, customer_id)
    if db.query(models.Order).filter(models.Order.customer_id == customer_id).first():
        raise HTTPException(status_code=400, detail='Cannot delete customer because orders exist')
    db.delete(customer)
    _commit(db)
    return {'message': 'Customer deleted successfully'}

# Orders
def list_orders(db: Session):
    return db.query(models.Order).options(
        joinedload(models.Order.customer),
        joinedload(models.Order.items).joinedload(models.OrderItem.product),
    ).order_by(models.Order.id.desc()).all()

def get_order(db: Session, order_id: int):
    order = db.query(models.Order).options(
        joinedload(models.Order.customer),
        joinedload(models.Order.items).joinedload(models.OrderItem.product),
    ).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail='Order not found')
    return order

def create_order(db: Session, data: schemas.OrderCreate):
    get_customer(db, data.customer_id)
    total = Decimal('0.00')
    order_items = []

    # Combine duplicate products in same request
    requested = {}
    for item in data.items:
        requested[item.product_id] = requested.get(item.product_id, 0) + item.quantity

    for product_id, quantity in requested.items():
        product = get_product(db, product_id)
        if product.stock < quantity:
            raise HTTPException(status_code=400, detail=f'Insufficient stock for {product.name}. Available: {product.stock}')
        product.stock -= quantity
        total += Decimal(product.price) * quantity
        order_items.append(models.OrderItem(product_id=product.id, quantity=quantity, unit_price=product.price))

    order = models.Order(customer_id=data.customer_id, total_amount=total, items=order_items)
    db.add(order)
    _commit(db)
    return get_order(db, order.id)

def update_order_status(db: Session, order_id: int, status: str):
    allowed_statuses = {'PLACED', 'COMPLETED', 'CANCELLED'}
    status = status.upper()
    if status not in allowed_statuses:
        raise HTTPException(status_code=400, detail='Invalid order status')

    order = db.query(models.Order).options(joinedload(models.Order.items)).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail='Order not found')

    if order.status == status:
        return get_order(db, order_id)

    if order.status == 'CANCELLED':
        raise HTTPException(status_code=400, detail='Cancelled orders cannot be changed again')

    if status == 'CANCELLED':
        for item in order.items:
            product = db.get(models.Product, item.product_id)
            if product:
                product.stock += item.quantity

    order.status = status
    _commit(db)
    return get_order(db, order_id)


def cancel_order(db: Session, order_id: int):
    return update_order_status(db, order_id, 'CANCELLED')


def delete_order(db: Session, order_id: int):
    order = db.query(models.Order).options(joinedload(models.Order.items)).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail='Order not found')
    if order.status != 'CANCELLED':
        for item in order.items:
            product = db.get(models.Product, item.product_id)
            if product:
                product.stock += item.quantity
    db.delete(order)
    _commit(db)
    return {'message': 'Order deleted successfully and stock restored'}


def dashboard_summary(db: Session):
    total_products = db.query(func.count(models.Product.id)).scalar() or 0
    total_customers = db.query(func.count(models.Customer.id)).scalar() or 0
    total_orders = db.query(func.count(models.Order.id)).scalar() or 0
    low_stock_products = db.query(func.count(models.Product.id)).filter(models.Product.stock < 5).scalar() or 0
    return {
        'totalProducts': total_products,
        'totalCustomers': total_customers,
        'totalOrders': total_orders,
        'lowStockProducts': low_stock_products,
    }
