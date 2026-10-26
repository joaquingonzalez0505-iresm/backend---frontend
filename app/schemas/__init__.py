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

    class Config:
        from_attributes = True

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

# --- PRODUCTOS ---
class ProductoBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    precio: float
    stock: int

class ProductoCreate(ProductoBase):
    pass

class ProductoResponse(ProductoBase):
    id: int
    imagen_url: Optional[str] = None

    class Config:
        from_attributes = True

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