from typing import List
from app.database import Base, engine, get_db
from app.models import Producto
from fastapi import Depends, FastAPI
from pydantic import BaseModel

# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session

Base.metadata.create_all(bind=engine)

app = FastAPI(title="E-Commerce API")


class ProductoSchema(BaseModel):
  id: int | None = None
  nombre: str
  precio_final: float
  cuotas_cantidad: int
  cuotas_valor: float
  garantia_meses: int
  stock: int

  class Config:
    from_attributes = True


@app.get("/productos", response_model=List[ProductoSchema])
def obtener_productos(db: Session = Depends(get_db)):
  return db.query(Producto).all()


@app.post("/productos", response_model=ProductoSchema)
def crear_producto(
    producto: ProductoSchema, db: Session = Depends(get_db)
):
  # Usamos Producto directamente
  db_producto = Producto(**producto.model_dump(exclude={"id"}))
  db.add(db_producto)
  db.commit()
  db.refresh(db_producto)
  return db_producto