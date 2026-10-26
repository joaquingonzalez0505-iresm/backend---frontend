from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Usuario
from app.schemas import UsuarioResponse
from app.core.security import obtener_usuario_actual

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

@router.get("/me", response_model=UsuarioResponse, summary="Obtener Mis Datos")
def obtener_mis_datos(usuario_actual: Usuario = Depends(obtener_usuario_actual)):
    email = usuario_actual.email.strip().lower()
    is_admin = (email == "joaquin@iresm.edu.ar") or (str(getattr(usuario_actual, "rol", "")).lower() == "admin")
    rol_val = "admin" if is_admin else (getattr(usuario_actual, "rol", "cliente") or "cliente")

    return {
        "id": usuario_actual.id,
        "email": usuario_actual.email,
        "nombre": usuario_actual.nombre,
        "rol": rol_val,
        "role": rol_val,
        "es_admin": is_admin,
        "is_admin": is_admin,
        "isAdmin": is_admin
    }

@router.delete("/me", summary="Anonimizar Mi Cuenta")
def anonimizar_cuenta(db: Session = Depends(get_db), usuario: Usuario = Depends(obtener_usuario_actual)):
    usuario.nombre = "Usuario Anonimizado"
    usuario.email = f"anonimo_{usuario.id}@deleted.com"
    db.commit()
    return {"mensaje": "Cuenta anonimizada correctamente"}