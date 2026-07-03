from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix='/orders', tags=['Orders'])

@router.get('/', response_model=list[schemas.OrderOut])
def list_orders(db: Session = Depends(get_db)):
    return crud.list_orders(db)

@router.get('/{order_id}', response_model=schemas.OrderOut)
def get_order(order_id: int, db: Session = Depends(get_db)):
    return crud.get_order(db, order_id)

@router.post('/', response_model=schemas.OrderOut, status_code=201)
def create_order(data: schemas.OrderCreate, db: Session = Depends(get_db)):
    return crud.create_order(db, data)

@router.patch('/{order_id}/status', response_model=schemas.OrderOut)
def update_order_status(order_id: int, data: schemas.OrderStatusUpdate, db: Session = Depends(get_db)):
    return crud.update_order_status(db, order_id, data.status)

@router.patch('/{order_id}/cancel', response_model=schemas.OrderOut)
def cancel_order(order_id: int, db: Session = Depends(get_db)):
    return crud.cancel_order(db, order_id)

@router.delete('/{order_id}')
def delete_order(order_id: int, db: Session = Depends(get_db)):
    return crud.delete_order(db, order_id)
