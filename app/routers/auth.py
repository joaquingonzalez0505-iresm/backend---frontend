from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Header, Body, Request, status
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.models import Usuario
from app.schemas.usuario import UsuarioCreate, UsuarioOut, Token
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token
)

router = APIRouter(prefix="/auth", tags=["Autenticación"])

@router.post("/register", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED)
@router.post("/register/", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED)
def registrar_usuario(user_in: UsuarioCreate, db: Session = Depends(get_db)):
    existente = db.query(Usuario).filter(Usuario.email == user_in.email).first()
    if existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo electrónico ya se encuentra registrado."
        )

    hashed_pwd = get_password_hash(user_in.password)
    nuevo_usuario = Usuario(
        nombre=user_in.nombre,
        email=user_in.email,
        hashed_password=hashed_pwd,
        rol=user_in.rol or "customer",
        acepto_tratamiento=user_in.acepto_tratamiento,
        fecha_consentimiento=datetime.now(timezone.utc),
        activo=True
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario

@router.post("/login", response_model=Token)
@router.post("/login/", response_model=Token)
async def iniciar_sesion(
    request: Request,
    db: Session = Depends(get_db)
):
    unauthorized_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales incorrectas: email o contraseña no válidos.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    username_input = None
    password_input = None

    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        try:
            body = await request.json()
            username_input = body.get("email") or body.get("username")
            password_input = body.get("password")
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cuerpo JSON no válido"
            )
    else:
        try:
            form_data = await request.form()
            username_input = form_data.get("username") or form_data.get("email")
            password_input = form_data.get("password")
        except Exception:
            pass

    if not username_input or not password_input:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Se requieren correo electrónico/usuario y contraseña."
        )

    user = db.query(Usuario).filter(Usuario.email == username_input).first()
    if not user or not user.activo:
        raise unauthorized_exception

    if not verify_password(password_input, user.hashed_password):
        raise unauthorized_exception

    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "rol": user.rol
    }
    
    access_token = create_access_token(data=token_data)
    refresh_token = create_refresh_token(data=token_data)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=UsuarioOut.model_validate(user)
    )

@router.post("/refresh", response_model=Token)
@router.post("/refresh/", response_model=Token)
def refrescar_token(
    refresh_token: Optional[str] = Body(None, embed=True),
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    token_str = None
    if refresh_token:
        token_str = refresh_token
    elif authorization and authorization.startswith("Bearer "):
        token_str = authorization.split(" ")[1]

    unauthorized_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token de refresco inválido o de tipo incorrecto",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not token_str:
        raise unauthorized_exception

    payload = decode_token(token_str)
    if not payload or payload.get("tipo") != "refresh":
        raise unauthorized_exception

    sub = payload.get("sub")
    if not sub:
        raise unauthorized_exception

    user = db.query(Usuario).filter(Usuario.id == int(sub)).first()
    if not user or not user.activo:
        raise unauthorized_exception

    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "rol": user.rol
    }
    new_access_token = create_access_token(data=token_data)
    new_refresh_token = create_refresh_token(data=token_data)

    return Token(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        user=UsuarioOut.model_validate(user)
    )

@router.get("/me", response_model=UsuarioOut)
@router.get("/me/", response_model=UsuarioOut)
def obtener_usuario_actual(current_user: Usuario = Depends(get_current_user)):
    return current_user
