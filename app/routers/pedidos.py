import uuid
from datetime import datetime, timezone
from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.models import Usuario, Pedido, ItemPedido, Producto, SolicitudRevocacion
from app.schemas.pedido import (
    PedidoCreate,
    PedidoOut,
    ItemIn,
    ItemOut,
    SolicitudArrepentimientoPublicaIn
)
from app.services.pedido_service import crear_pedido_service

router = APIRouter(tags=["Pedidos"])


def _normalizar_item(raw: Any) -> ItemIn:
    """Convierte un dict raw (con cualquier variante de campos) en ItemIn."""
    if isinstance(raw, dict):
        return ItemIn(
            producto_id=raw.get("producto_id") or raw.get("id") or raw.get("product_id"),
            cantidad=raw.get("cantidad") or raw.get("quantity") or 1,
        )
    return raw


def _construir_pedido_out(pedido: Pedido) -> PedidoOut:
    items_out = []
    for item in pedido.items:
        prod_nombre = item.producto.nombre if item.producto else None
        items_out.append(ItemOut(
            id=item.id,
            producto_id=item.producto_id,
            cantidad=item.cantidad,
            precio_unitario=float(item.precio_unitario),
            producto_nombre=prod_nombre
        ))

    codigo_rev = None
    if pedido.solicitud_revocacion:
        codigo_rev = pedido.solicitud_revocacion.codigo

    return PedidoOut(
        id=pedido.id,
        usuario_id=pedido.usuario_id,
        estado=pedido.estado,
        total=float(pedido.total),
        fecha_creacion=pedido.fecha_creacion,
        codigo_solicitud_revocacion=codigo_rev,
        items=items_out
    )


@router.post("/pedidos", response_model=PedidoOut, status_code=status.HTTP_201_CREATED)
@router.post("/pedidos/", response_model=PedidoOut, status_code=status.HTTP_201_CREATED)
async def crear_pedido(
    request: Request,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    # ── Parsear body de forma flexible ──────────────────────────────────────
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El cuerpo de la petición no es JSON válido"
        )

    # Log de depuración en terminal
    print("=== POST /pedidos/ ── Payload recibido:", payload)

    items_raw: list = []

    if isinstance(payload, list):
        # Formato: array directo [{ producto_id, cantidad }, ...]
        items_raw = payload

    elif isinstance(payload, dict):
        # Formato: { items: [...] } o { productos: [...] }
        items_raw = (
            payload.get("items")
            or payload.get("productos")
            or payload.get("products")
            or []
        )
        # Si viene como objeto único { producto_id, cantidad }
        if not items_raw and ("producto_id" in payload or "id" in payload):
            items_raw = [payload]

    if not items_raw:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No se encontraron ítems en el pedido. "
                   "Enviá un array [{ producto_id, cantidad }] o { \"items\": [...] }"
        )

    # Normalizar cada ítem aceptando producto_id / id / product_id
    items_in: List[ItemIn] = []
    for raw in items_raw:
        try:
            items_in.append(_normalizar_item(raw))
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Ítem inválido {raw}: {e}"
            )

    print(f"=== Ítems normalizados: {[{'producto_id': i.producto_id, 'cantidad': i.cantidad} for i in items_in]}")

    nuevo_pedido = crear_pedido_service(db, current_user, items_in)
    return _construir_pedido_out(nuevo_pedido)


@router.get("/pedidos", response_model=List[PedidoOut])
@router.get("/pedidos/", response_model=List[PedidoOut])
@router.get("/pedidos/mios", response_model=List[PedidoOut])
@router.get("/pedidos/mios/", response_model=List[PedidoOut])
def listar_mis_pedidos(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    pedidos = (
        db.query(Pedido)
        .filter(Pedido.usuario_id == current_user.id)
        .order_by(Pedido.fecha_creacion.desc())
        .all()
    )
    return [_construir_pedido_out(p) for p in pedidos]


@router.get("/pedidos/{pedido_id}", response_model=PedidoOut)
def obtener_pedido(
    pedido_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido no encontrado")

    if pedido.usuario_id != current_user.id and current_user.rol != "admin":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido no encontrado")

    return _construir_pedido_out(pedido)


def _ejecutar_revocacion(db: Session, pedido: Pedido, usuario_id: int) -> str:
    if pedido.estado == "cancelado":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El pedido ya se encuentra cancelado"
        )

    ahora = datetime.now(timezone.utc)
    fecha_creacion_utc = pedido.fecha_creacion
    if fecha_creacion_utc.tzinfo is None:
        fecha_creacion_utc = fecha_creacion_utc.replace(tzinfo=timezone.utc)

    dias_transcurridos = (ahora - fecha_creacion_utc).total_seconds() / 86400.0
    if dias_transcurridos > 10.0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El plazo de 10 días corridos para revocar la compra ha expirado"
        )

    try:
        for item in pedido.items:
            if item.producto:
                item.producto.stock += item.cantidad

        pedido.estado = "cancelado"
        fecha_str = ahora.strftime("%Y%m%d")
        token_str = uuid.uuid4().hex[:6].upper()
        codigo_solicitud = f"ARR-{fecha_str}-{token_str}"

        solicitud = SolicitudRevocacion(
            codigo=codigo_solicitud,
            pedido_id=pedido.id,
            usuario_id=usuario_id,
            creada_en=ahora
        )
        db.add(solicitud)
        db.commit()
        db.refresh(pedido)
        return codigo_solicitud

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en la transacción de revocación: {str(e)}"
        )


@router.post("/pedidos/{pedido_id}/revocacion")
@router.post("/pedidos/{pedido_id}/revocacion/")
@router.post("/pedidos/{pedido_id}/revocar")
@router.post("/pedidos/{pedido_id}/revocar/")
def revocar_pedido_autenticado(
    pedido_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if not pedido or pedido.usuario_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido no encontrado")

    codigo = _ejecutar_revocacion(db, pedido, current_user.id)
    return {
        "mensaje": "Solicitud de revocación registrada exitosamente",
        "codigo_solicitud": codigo,
        "pedido_id": pedido.id,
        "nuevo_estado": pedido.estado
    }


@router.post("/arrepentimiento")
@router.post("/arrepentimiento/")
def revocar_pedido_publico(
    datos: SolicitudArrepentimientoPublicaIn,
    db: Session = Depends(get_db)
):
    pedido = db.query(Pedido).filter(Pedido.id == datos.pedido_id).first()
    if not pedido or not pedido.usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido no encontrado")

    if pedido.usuario.email.lower() != datos.email.lower():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido no encontrado")

    codigo = _ejecutar_revocacion(db, pedido, pedido.usuario_id)
    return {
        "mensaje": "Solicitud de arrepentimiento registrada exitosamente",
        "codigo_solicitud": codigo,
        "pedido_id": pedido.id,
        "nuevo_estado": pedido.estado
    }
