from fastapi import FastAPI, Depends, Query
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import engine, Base, get_db
from app import schemas
from app.services import productos as productos_service

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/productos", response_model=List[schemas.ProductoOut])
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

@app.post("/productos", response_model=schemas.ProductoOut)
def crear_producto(
    producto: schemas.ProductoCreate,
    db: Session = Depends(get_db)
):
    return productos_service.crear_producto(db=db, producto=producto)