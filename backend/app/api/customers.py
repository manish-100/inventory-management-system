from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix='/customers', tags=['Customers'])

@router.get('/', response_model=list[schemas.CustomerOut])
def list_customers(search: Optional[str] = Query(default=None), db: Session = Depends(get_db)):
    return crud.list_customers(db, search)

@router.get('/{customer_id}', response_model=schemas.CustomerOut)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    return crud.get_customer(db, customer_id)

@router.post('/', response_model=schemas.CustomerOut, status_code=201)
def create_customer(data: schemas.CustomerCreate, db: Session = Depends(get_db)):
    return crud.create_customer(db, data)

@router.put('/{customer_id}', response_model=schemas.CustomerOut)
def update_customer(customer_id: int, data: schemas.CustomerUpdate, db: Session = Depends(get_db)):
    return crud.update_customer(db, customer_id, data)

@router.delete('/{customer_id}')
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    return crud.delete_customer(db, customer_id)
