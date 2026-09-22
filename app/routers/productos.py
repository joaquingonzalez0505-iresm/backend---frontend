# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, Query
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
from typing import List, Optional

from app.dependencies import get_db
from app import schemas
from app.services import productos as productos_service

router = APIRouter(prefix="/productos", tags=["Productos"])
# app/routers/productos.py

@router.get("", response_model=List[schemas.ProductoOut])   # <-- Agrega esta línea
@router.get("/", response_model=List[schemas.ProductoOut])  # <-- Mantén esta línea
def obtener_productos(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    nombre: Optional[str] = None,
    precio_max: Optional[float] = None,
    db: Session = Depends(get_db)
):
    return productos_service.listar_productos(
        db=db, skip=skip, limit=limit, nombre=nombre, precio_max=precio_max
    )
@router.get("", response_model=List[schemas.ProductoOut])  # Sin la barra "/"
def obtener_productos(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    nombre: Optional[str] = None,
    precio_max: Optional[float] = None,
    db: Session = Depends(get_db)
):
    return productos_service.listar_productos(
        db=db, skip=skip, limit=limit, nombre=nombre, precio_max=precio_max
    )