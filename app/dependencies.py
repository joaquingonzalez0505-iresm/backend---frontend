from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.core.security import decode_token
from app.models import Usuario

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Usuario:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception

    # Check sub (user id) or email in token payload
    sub = payload.get("sub")
    email = payload.get("email")
    
    user = None
    if sub and str(sub).isdigit():
        user = db.query(Usuario).filter(Usuario.id == int(sub)).first()
    elif email:
        user = db.query(Usuario).filter(Usuario.email == email).first()

    if user is None:
        raise credentials_exception

    # Clase 9: Rechazar usuarios desactivados/dados de baja
    if not user.activo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario inactivo o dado de baja",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user

def require_admin(current_user: Usuario = Depends(get_current_user)) -> Usuario:
    if current_user.rol != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado: se requieren permisos de administrador"
        )
    return current_user
