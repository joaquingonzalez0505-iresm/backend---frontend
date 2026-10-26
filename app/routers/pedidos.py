from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Pedido

router = APIRouter(prefix="/pedidos", tags=["Pedidos"])

@router.get("", summary="Listar Pedidos")
@router.get("/", include_in_schema=False)
@router.get("/admin", include_in_schema=False)
@router.get("/todos", include_in_schema=False)
def listar_pedidos(db: Session = Depends(get_db)):
    try:
        pedidos = db.query(Pedido).all()
        res = []
        for p in pedidos:
            res.append({
                "id": p.id,
                "usuario_id": getattr(p, "usuario_id", 1),
                "total": float(getattr(p, "total", 0.0) or 0.0),
                "estado": getattr(p, "estado", "pendiente") or "pendiente"
            })
        return res
    except Exception as e:
        print(f"Error consultando pedidos: {e}")
        return []

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

    try:
        nuevo_pedido = Pedido(
            usuario_id=data.get("usuario_id", 1),
            total=total,
            estado=data.get("estado", "pendiente")
        )
        db.add(nuevo_pedido)
        db.commit()
        db.refresh(nuevo_pedido)
        return {
            "id": nuevo_pedido.id,
            "usuario_id": nuevo_pedido.usuario_id,
            "total": nuevo_pedido.total,
            "estado": nuevo_pedido.estado
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error creando pedido: {str(e)}")