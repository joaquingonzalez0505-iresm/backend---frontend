from typing import Optional
from pydantic import BaseModel

class ProductoCreate(BaseModel):
    nombre: str
    precio_final: float
    cuotas_cantidad: int = 1
    cuotas_valor: float = 0.0
    garantia_meses: int = 0
    stock: int = 0
    imagen: Optional[str] = None
    imagen_url: Optional[str] = None

class ProductoOut(ProductoCreate):
    id: int

    class Config:
        from_attributes = True
