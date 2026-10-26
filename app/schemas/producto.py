from typing import Optional
from pydantic import BaseModel

class ProductoCreate(BaseModel):
    nombre: Optional[str] = "Producto"
    descripcion: Optional[str] = ""
    precio: Optional[float] = 0.0
    precio_final: Optional[float] = 0.0
    cuotas_cantidad: Optional[int] = 1
    cuotas_valor: Optional[float] = 0.0
    garantia_meses: Optional[int] = 0
    stock: Optional[int] = 0
    imagen: Optional[str] = ""
    imagen_url: Optional[str] = ""

    class Config:
        extra = "allow"

class ProductoOut(ProductoCreate):
    id: int

    class Config:
        from_attributes = True
        extra = "allow"

