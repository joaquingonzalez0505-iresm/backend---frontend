from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Usuario
from app.schemas import UsuarioCreate, UsuarioResponse, Token
from app.core.security import crear_token_acceso, obtener_usuario_actual, hash_password, verificar_password

router = APIRouter(prefix="/auth", tags=["Autenticación"])

def construir_respuesta_usuario(usuario: Usuario) -> Dict[str, Any]:
    email_clean = usuario.email.strip().lower()
    is_admin = (email_clean == "joaquin@iresm.edu.ar") or (str(getattr(usuario, "rol", "")).lower() == "admin")
    rol_val = "admin" if is_admin else (getattr(usuario, "rol", "cliente") or "cliente")
    
    return {
        "id": usuario.id,
        "email": usuario.email,
        "nombre": usuario.nombre,
        "rol": rol_val,
        "role": rol_val,
        "es_admin": is_admin,
        "is_admin": is_admin,
        "isAdmin": is_admin
    }

@router.post("/register", response_model=UsuarioResponse, summary="Registrar Usuario")
@router.post("/register/", response_model=UsuarioResponse, include_in_schema=False)
def registrar_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    db_usuario = db.query(Usuario).filter(Usuario.email == usuario.email).first()
    if db_usuario:
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    
    email_clean = usuario.email.strip().lower()
    rol_final = "admin" if email_clean == "joaquin@iresm.edu.ar" else (getattr(usuario, 'rol', 'cliente') or 'cliente')

    nuevo_usuario = Usuario(
        email=usuario.email,
        nombre=usuario.nombre,
        hashed_password=hash_password(usuario.password),
        rol=rol_final
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return construir_respuesta_usuario(nuevo_usuario)

@router.post("/login", response_model=Token, summary="Iniciar Sesión")
@router.post("/login/", response_model=Token, include_in_schema=False)
async def iniciar_sesion(request: Request, db: Session = Depends(get_db)):
    content_type = request.headers.get("content-type", "")
    
    if "application/json" in content_type:
        try:
            data = await request.json()
        except Exception:
            data = {}
        email = data.get("email") or data.get("username")
        password = data.get("password")
    else:
        try:
            form = await request.form()
        except Exception:
            form = {}
        email = form.get("username") or form.get("email")
        password = form.get("password")

    if not email or not password:
        raise HTTPException(status_code=400, detail="Email y contraseña requeridos")

    email_clean = str(email).strip().lower()
    password_str = str(password)
    usuario = db.query(Usuario).filter(Usuario.email == email_clean).first()

    # Si es Joaquin y la clave es 123, forzar creación / actualización con rol admin
    if email_clean == "joaquin@iresm.edu.ar" and password_str == "123":
        if not usuario:
            usuario = Usuario(
                email="joaquin@iresm.edu.ar",
                nombre="Joaquin Admin",
                hashed_password=hash_password("123"),
                rol="admin"
            )
            db.add(usuario)
            db.commit()
            db.refresh(usuario)
        else:
            usuario.hashed_password = hash_password("123")
            usuario.rol = "admin"
            db.commit()
    else:
        if not usuario or not verificar_password(password_str, usuario.hashed_password):
            raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    access_token = crear_token_acceso(data={"sub": usuario.email})
    user_dict = construir_respuesta_usuario(usuario)

    return {
        "access_token": access_token,
        "token": access_token,
        "token_type": "bearer",
        "user": user_dict,
        "usuario": user_dict,
        "rol": user_dict["rol"],
        "role": user_dict["role"],
        "es_admin": user_dict["es_admin"],
        "is_admin": user_dict["is_admin"],
        "isAdmin": user_dict["isAdmin"]
    }

@router.get("/me", response_model=UsuarioResponse, summary="Obtener Usuario Actual")
@router.get("/me/", response_model=UsuarioResponse, include_in_schema=False)
def obtener_mi_usuario(usuario_actual: Usuario = Depends(obtener_usuario_actual)):
    return construir_respuesta_usuario(usuario_actual)