from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Usuario
from app.schemas import UsuarioResponse
from app.core.security import obtener_usuario_actual

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

def construir_respuesta_usuario(usuario: Usuario) -> Dict[str, Any]:
    email_clean = usuario.email.strip().lower()
    is_admin = (email_clean == "joaquin@iresm.edu.ar") or (str(getattr(usuario, "rol", "")).strip().lower() == "admin")
    rol_val = "admin" if is_admin else (str(getattr(usuario, "rol", "cliente") or "cliente").strip().lower())
    nombre_val = usuario.nombre or ("Joaquin Admin" if is_admin else "Usuario")

    return {
        "id": usuario.id,
        "email": usuario.email,
        "nombre": nombre_val,
        "rol": rol_val,
        "role": rol_val,
        "es_admin": is_admin,
        "is_admin": is_admin,
        "isAdmin": is_admin
    }

def construir_respuesta_enriquecida(usuario: Usuario) -> Dict[str, Any]:
    user_dict = construir_respuesta_usuario(usuario)
    return {
        **user_dict,
        "user": user_dict,
        "usuario": user_dict,
        "rol": user_dict["rol"],
        "role": user_dict["role"],
        "es_admin": user_dict["es_admin"],
        "is_admin": user_dict["is_admin"],
        "isAdmin": user_dict["isAdmin"]
    }

@router.get("/me", response_model=UsuarioResponse, summary="Obtener Mis Datos")
@router.get("/me/", response_model=UsuarioResponse, include_in_schema=False)
def obtener_mis_datos(usuario_actual: Usuario = Depends(obtener_usuario_actual), db: Session = Depends(get_db)):
    if usuario_actual.email.strip().lower() == "joaquin@iresm.edu.ar" and usuario_actual.rol != "admin":
        usuario_actual.rol = "admin"
        db.commit()
        db.refresh(usuario_actual)
    return construir_respuesta_enriquecida(usuario_actual)


@router.delete("/me", summary="Anonimizar Mi Cuenta")
def anonimizar_cuenta(db: Session = Depends(get_db), usuario: Usuario = Depends(obtener_usuario_actual)):
    usuario.nombre = "Usuario Anonimizado"
    usuario.email = f"anonimo_{usuario.id}@deleted.com"
    db.commit()
    return {"mensaje": "Cuenta anonimizada correctamente"}