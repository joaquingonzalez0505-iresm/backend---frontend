from pydantic import BaseModel
from typing import Optional, List, Dict, Any

# --- USUARIOS ---
class UsuarioBase(BaseModel):
    email: str
    nombre: Optional[str] = None

class UsuarioCreate(UsuarioBase):
    password: str
    rol: Optional[str] = "cliente"

class UsuarioResponse(UsuarioBase):
    id: int
    rol: Optional[str] = "cliente"
    role: Optional[str] = "cliente"
    es_admin: Optional[bool] = False
    is_admin: Optional[bool] = False
    isAdmin: Optional[bool] = False
    user: Optional[Dict[str, Any]] = None
    usuario: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True
        extra = "allow"

# --- TOKEN DE AUTENTICACIÓN ---
class Token(BaseModel):
    access_token: str
    token: Optional[str] = None
    token_type: str = "bearer"
    user: Optional[Dict[str, Any]] = None
    usuario: Optional[Dict[str, Any]] = None
    rol: Optional[str] = None
    role: Optional[str] = None
    es_admin: Optional[bool] = None
    is_admin: Optional[bool] = None
    isAdmin: Optional[bool] = None

    class Config:
        extra = "allow"

# --- PRODUCTOS ---
class ProductoBase(BaseModel):
    nombre: Optional[str] = "Producto StickerLab"
    descripcion: Optional[str] = ""
    description: Optional[str] = ""
    precio: Optional[float] = 0.0
    precio_final: Optional[float] = 0.0
    precioFinal: Optional[float] = 0.0
    cuotas: Optional[int] = 1
    cuotas_cantidad: Optional[int] = 1
    cuotas_valor: Optional[float] = 0.0
    garantia_meses: Optional[int] = 0
    stock: Optional[int] = 0
    imagen: Optional[str] = ""
    imagen_url: Optional[str] = ""
    image: Optional[str] = ""

    class Config:
        extra = "allow"

class ProductoCreate(ProductoBase):
    pass

class ProductoResponse(ProductoBase):
    id: int

    class Config:
        from_attributes = True
        extra = "allow"

# --- PEDIDOS ---
class PedidoCreate(BaseModel):
    total: float

class PedidoResponse(BaseModel):
    id: int
    usuario_id: int
    total: float
    estado: str

    class Config:
        from_attributes = True
        extra = "allow"