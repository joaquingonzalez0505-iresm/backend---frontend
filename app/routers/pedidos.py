from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Pedido, Usuario
from app.core.security import decodificar_token

router = APIRouter(prefix="/pedidos", tags=["Pedidos"])

def obtener_usuario_id_de_request(request: Request, db: Session, data: dict = None) -> Optional[int]:
    data = data or {}
    
    # 1. Intentar obtener el usuario desde el Token Bearer de la sesión
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        try:
            token = auth_header.split(" ")[1]
            payload = decodificar_token(token)
            if payload and "sub" in payload:
                u = db.query(Usuario).filter(Usuario.email == payload["sub"].strip().lower()).first()
                if u:
                    return u.id
        except Exception:
            pass

    # 2. Intentar obtener por ID explícito en la petición
    uid = data.get("usuario_id") or data.get("usuarioId") or data.get("user_id") or data.get("userId")
    if uid:
        try:
            return int(uid)
        except (ValueError, TypeError):
            pass

    # 3. Intentar buscar por Email enviado en la petición
    email = data.get("email") or data.get("usuario_email") or data.get("user_email")
    if email:
        try:
            u = db.query(Usuario).filter(Usuario.email == str(email).strip().lower()).first()
            if u:
                return u.id
        except Exception:
            pass

    return None

def formatear_pedido(p: Pedido) -> dict:
    uid = getattr(p, "usuario_id", 1) or 1
    tot = float(getattr(p, "total", 0.0) or 0.0)
    est = getattr(p, "estado", "pendiente") or "pendiente"
    return {
        "id": p.id,
        "usuario_id": uid,
        "usuarioId": uid,
        "user_id": uid,
        "userId": uid,
        "total": tot,
        "monto": tot,
        "precio": tot,
        "estado": est,
        "status": est
    }

@router.get("", summary="Listar Pedidos")
@router.get("/", include_in_schema=False)
@router.get("/admin", include_in_schema=False)
@router.get("/todos", include_in_schema=False)
@router.get("/mis-pedidos", include_in_schema=False)
@router.get("/me", include_in_schema=False)
@router.get("/usuario", include_in_schema=False)
def listar_pedidos(
    request: Request,
    usuario_id: Optional[int] = None,
    email: Optional[str] = None,
    db: Session = Depends(get_db)
):
    path = request.url.path.rstrip("/")
    is_me_endpoint = path.endswith("/mis-pedidos") or path.endswith("/me")
    
    req_user_id = obtener_usuario_id_de_request(request, db)
    query = db.query(Pedido)
    
    # Si la consulta viene de una pestaña de mis pedidos
    if is_me_endpoint:
        target_id = req_user_id or usuario_id
        if target_id:
            query = query.filter(Pedido.usuario_id == target_id)
        elif email:
            u = db.query(Usuario).filter(Usuario.email == email.strip().lower()).first()
            if u:
                query = query.filter(Pedido.usuario_id == u.id)
    elif usuario_id is not None:
        query = query.filter(Pedido.usuario_id == usuario_id)
    elif email:
        u = db.query(Usuario).filter(Usuario.email == email.strip().lower()).first()
        if u:
            query = query.filter(Pedido.usuario_id == u.id)

    pedidos = query.all()
    return [formatear_pedido(p) for p in pedidos]

@router.get("/usuario/{user_id}", summary="Obtener Pedidos por Usuario ID")
@router.get("/user/{user_id}", include_in_schema=False)
def obtener_pedidos_usuario(user_id: int, db: Session = Depends(get_db)):
    pedidos = db.query(Pedido).filter(Pedido.usuario_id == user_id).all()
    return [formatear_pedido(p) for p in pedidos]

@router.post("", summary="Crear Pedido")
@router.post("/", include_in_schema=False)
async def crear_pedido(request: Request, db: Session = Depends(get_db)):
    data = {}
    try:
        data = await request.json()
    except Exception:
        try:
            form = await request.form()
            data = dict(form)
        except Exception:
            data = {}

    total_val = data.get("total") or data.get("monto") or data.get("subtotal") or 0.0
    try:
        total = float(str(total_val).replace(",", "."))
    except Exception:
        total = 0.0

    user_id = obtener_usuario_id_de_request(request, db, data) or 1

    try:
        nuevo_pedido = Pedido(
            usuario_id=user_id,
            total=total,
            estado=data.get("estado", "pendiente")
        )
        db.add(nuevo_pedido)
        db.commit()
        db.refresh(nuevo_pedido)
        return formatear_pedido(nuevo_pedido)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error creando pedido: {str(e)}")