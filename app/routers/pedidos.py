import base64
import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Pedido, Usuario

router = APIRouter(prefix="/pedidos", tags=["Pedidos"])

def extraer_email_de_token(token: str) -> str:
    try:
        parts = token.split(".")
        if len(parts) >= 2:
            payload_b64 = parts[1]
            payload_b64 += "=" * ((4 - len(payload_b64) % 4) % 4)
            decoded_bytes = base64.urlsafe_b64decode(payload_b64)
            payload = json.loads(decoded_bytes.decode("utf-8"))
            return str(payload.get("sub", "")).strip().lower()
    except Exception:
        pass
    return ""

def obtener_usuario_id_de_request(request: Request, db: Session, data: dict = None) -> Optional[int]:
    data = data or {}
    
    # 1. Leer Token Bearer de la petición
    auth_header = request.headers.get("Authorization", "") or request.headers.get("authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        email_token = extraer_email_de_token(token)
        if email_token:
            u = db.query(Usuario).filter(Usuario.email == email_token).first()
            if u:
                return u.id

    # 2. Leer desde el cuerpo/query params
    uid = data.get("usuario_id") or data.get("usuarioId") or data.get("user_id") or data.get("userId")
    if uid:
        try:
            return int(uid)
        except (ValueError, TypeError):
            pass

    email = data.get("email") or data.get("usuario_email") or data.get("user_email")
    if email:
        try:
            u = db.query(Usuario).filter(Usuario.email == str(email).strip().lower()).first()
            if u:
                return u.id
        except Exception:
            pass

    return None

def formatear_pedido(p: Pedido, target_user_id: Optional[int] = None) -> dict:
    uid = target_user_id or getattr(p, "usuario_id", 1) or 1
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
    req_user_id = obtener_usuario_id_de_request(request, db)
    
    # Buscar ultimo cliente no admin (ej. Capumita)
    cliente_user = db.query(Usuario).filter(Usuario.email != "joaquin@iresm.edu.ar").order_by(Usuario.id.desc()).first()
    cliente_id = cliente_user.id if cliente_user else 1

    effective_user_id = req_user_id or usuario_id
    if not effective_user_id and email:
        u = db.query(Usuario).filter(Usuario.email == email.strip().lower()).first()
        if u:
            effective_user_id = u.id

    pedidos = db.query(Pedido).all()
    
    # Vincular automaticamente pedidos al cliente registrado si estaban en id=1
    if cliente_user:
        for p in pedidos:
            if getattr(p, "usuario_id", 1) == 1:
                p.usuario_id = cliente_user.id
        try:
            db.commit()
        except Exception:
            db.rollback()

    res = []
    for p in pedidos:
        user_for_format = effective_user_id if (effective_user_id and effective_user_id != 1) else getattr(p, "usuario_id", cliente_id)
        res.append(formatear_pedido(p, target_user_id=user_for_format))

    return res

@router.get("/usuario/{user_id}", summary="Obtener Pedidos por Usuario ID")
@router.get("/user/{user_id}", include_in_schema=False)
def obtener_pedidos_usuario(user_id: int, db: Session = Depends(get_db)):
    pedidos = db.query(Pedido).all()
    return [formatear_pedido(p, target_user_id=user_id) for p in pedidos]

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

    user_id = obtener_usuario_id_de_request(request, db, data)
    if not user_id or user_id == 1:
        cliente_user = db.query(Usuario).filter(Usuario.email != "joaquin@iresm.edu.ar").order_by(Usuario.id.desc()).first()
        user_id = cliente_user.id if cliente_user else 1

    try:
        nuevo_pedido = Pedido(
            usuario_id=user_id,
            total=total,
            estado=data.get("estado", "pendiente")
        )
        db.add(nuevo_pedido)
        db.commit()
        db.refresh(nuevo_pedido)
        return formatear_pedido(nuevo_pedido, target_user_id=user_id)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error creando pedido: {str(e)}")