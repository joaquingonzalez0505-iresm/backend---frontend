from pydantic import BaseModel, ConfigDict

class ProductoBase(BaseModel):
    nombre: str
    precio_final: float
    cuotas_cantidad: int
    cuotas_valor: float
    garantia_meses: int
    stock: int

class ProductoCreate(ProductoBase):
    pass

class ProductoResponse(ProductoBase):
    id: int

    model_config = ConfigDict(from_attributes=True)