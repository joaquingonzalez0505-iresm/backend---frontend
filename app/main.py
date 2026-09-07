from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from typing import List

from .database import engine, Base, get_db
from . import models
from .schemas import ProductoCreate, ProductoResponse

# Crear las tablas en la base de datos al arrancar
Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/productos", response_model=List[ProductoResponse])
def obtener_productos(db: Session = Depends(get_db)):
    return db.query(models.Producto).all()

@app.post("/productos", response_model=ProductoResponse)
def crear_producto(producto: ProductoCreate, db: Session = Depends(get_db)):
    datos = producto.model_dump() if hasattr(producto, "model_dump") else producto.dict()
    nuevo_producto = models.Producto(**datos)
    db.add(nuevo_producto)
    db.commit()
    db.refresh(nuevo_producto)
    return nuevo_producto