from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models import Pedido, Usuario
from app.schemas import PedidoCreate, PedidoResponse
from app.core.security import obtener_usuario_actual

router = APIRouter(prefix="/pedidos", tags=["Pedidos"])

class ArrepentimientoSchema(BaseModel):
    pedido_id: int
    email: str

@router.get("", response_model=List[PedidoResponse], summary="Obtener Pedidos")
def listar_mis_pedidos(db: Session = Depends(get_db), usuario: Usuario = Depends(obtener_usuario_actual)):
    return db.query(Pedido).filter(Pedido.usuario_id == usuario.id).all()

@router.post("", response_model=PedidoResponse, summary="Crear Pedido")
def crear_pedido(pedido: PedidoCreate, db: Session = Depends(get_db), usuario: Usuario = Depends(obtener_usuario_actual)):
    nuevo_pedido = Pedido(usuario_id=usuario.id, total=pedido.total, estado="pendiente")
    db.add(nuevo_pedido)
    db.commit()
    db.refresh(nuevo_pedido)
    return nuevo_pedido

@router.post("/arrepentimiento", summary="Revocar Pedido (Público)")
def revocar_pedido_publico(datos: ArrepentimientoSchema, db: Session = Depends(get_db)):
    pedido = db.query(Pedido).filter(Pedido.id == datos.pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    pedido.estado = "cancelado"
    db.commit()
    return {"mensaje": f"El pedido #{datos.pedido_id} ha sido revocado exitosamente."}