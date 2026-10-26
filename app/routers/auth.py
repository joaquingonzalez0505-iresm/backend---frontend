from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Usuario
from app.schemas import UsuarioCreate, UsuarioResponse, Token
from app.core.security import crear_token_acceso, obtener_usuario_actual, hash_password, verificar_password

router = APIRouter(prefix="/auth", tags=["Autenticación"])

@router.post("/register", response_model=UsuarioResponse, summary="Registrar Usuario")
def registrar_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    db_usuario = db.query(Usuario).filter(Usuario.email == usuario.email).first()
    if db_usuario:
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    
    email_clean = usuario.email.strip().lower()
    rol_final = "admin" if email_clean == "joaquin@iresm.edu.ar" else getattr(usuario, 'rol', 'cliente')

    nuevo_usuario = Usuario(
        email=usuario.email,
        nombre=usuario.nombre,
        hashed_password=hash_password(usuario.password),
        rol=rol_final
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario

@router.post("/login", response_model=Token, summary="Iniciar Sesión")
async def iniciar_sesion(request: Request, db: Session = Depends(get_db)):
    content_type = request.headers.get("content-type", "")
    
    if "application/json" in content_type:
        data = await request.json()
        email = data.get("email") or data.get("username")
        password = data.get("password")
    else:
        form = await request.form()
        email = form.get("username") or form.get("email")
        password = form.get("password")

    if not email or not password:
        raise HTTPException(status_code=400, detail="Email y contraseña requeridos")

    email_clean = email.strip().lower()
    usuario = db.query(Usuario).filter(Usuario.email == email_clean).first()

    # Si es Joaquin y la clave es 123, forzar ingreso e igualar hash si hace falta
    if email_clean == "joaquin@iresm.edu.ar" and password == "123":
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
        if not usuario or not verificar_password(password, usuario.hashed_password):
            raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    access_token = crear_token_acceso(data={"sub": usuario.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UsuarioResponse, summary="Obtener Usuario Actual")
def obtener_mi_usuario(usuario_actual: Usuario = Depends(obtener_usuario_actual)):
    is_admin = (usuario_actual.email.strip().lower() == "joaquin@iresm.edu.ar") or (str(getattr(usuario_actual, "rol", "")).lower() == "admin")
    
    rol_val = "admin" if is_admin else getattr(usuario_actual, "rol", "cliente")
    
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