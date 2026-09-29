from datetime import datetime
from typing import Optional
from pydantic import BaseModel, field_validator

class UsuarioCreate(BaseModel):
    nombre: str
    email: str
    password: str
    acepto_tratamiento: bool = True
    rol: Optional[str] = "customer"

    @field_validator("acepto_tratamiento")
    @classmethod
    def validar_consentimiento(cls, v: bool) -> bool:
        if not v:
            raise ValueError("Debe aceptar el tratamiento de datos personales para poder registrarse.")
        return v

class LoginRequest(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None
    password: str

class PerfilUpdate(BaseModel):
    nombre: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None

class UsuarioOut(BaseModel):
    id: int
    nombre: str
    email: str
    rol: str
    acepto_tratamiento: bool
    fecha_consentimiento: Optional[datetime] = None
    activo: bool = True
    fecha_baja: Optional[datetime] = None

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    user: Optional[UsuarioOut] = None

# Aliases for backwards compatibility
UserRegister = UsuarioCreate
UserOut = UsuarioOut
