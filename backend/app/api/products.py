from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix='/products', tags=['Products'])

@router.get('/', response_model=list[schemas.ProductOut])
def list_products(search: Optional[str] = Query(default=None), db: Session = Depends(get_db)):
    return crud.list_products(db, search)

@router.get('/{product_id}', response_model=schemas.ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    return crud.get_product(db, product_id)

@router.post('/', response_model=schemas.ProductOut, status_code=201)
def create_product(data: schemas.ProductCreate, db: Session = Depends(get_db)):
    return crud.create_product(db, data)

@router.put('/{product_id}', response_model=schemas.ProductOut)
def update_product(product_id: int, data: schemas.ProductUpdate, db: Session = Depends(get_db)):
    return crud.update_product(db, product_id, data)

@router.delete('/{product_id}')
def delete_product(product_id: int, db: Session = Depends(get_db)):
    return crud.delete_product(db, product_id)
