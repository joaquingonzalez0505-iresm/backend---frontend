from datetime import datetime, timezone
from typing import List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import Pedido, ItemPedido, Producto, Usuario
from app.schemas.pedido import ItemIn

def crear_pedido_service(db: Session, current_user: Usuario, items_in: List[ItemIn]) -> Pedido:
    if not items_in:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El carrito no contiene productos")

    try:
        total_acumulado = 0.0
        items_a_crear = []

        for item in items_in:
            prod = db.query(Producto).filter(Producto.id == item.producto_id).first()
            if not prod:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Producto con ID {item.producto_id} no encontrado"
                )

            if prod.stock < item.cantidad:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Stock insuficiente para el producto '{prod.nombre}'. Unidades disponibles: {prod.stock}"
                )

            # Descontar stock
            prod.stock -= item.cantidad

            # Congelar precio unitario
            precio_congelado = float(prod.precio_final)
            subtotal = precio_congelado * item.cantidad
            total_acumulado += subtotal

            items_a_crear.append({
                "producto_id": prod.id,
                "cantidad": item.cantidad,
                "precio_unitario": precio_congelado
            })

        nuevo_pedido = Pedido(
            usuario_id=current_user.id,
            estado="pendiente",
            total=total_acumulado,
            fecha_creacion=datetime.now(timezone.utc)
        )
        db.add(nuevo_pedido)
        db.flush()

        for item_data in items_a_crear:
            item_obj = ItemPedido(
                pedido_id=nuevo_pedido.id,
                producto_id=item_data["producto_id"],
                cantidad=item_data["cantidad"],
                precio_unitario=item_data["precio_unitario"]
            )
            db.add(item_obj)

        db.commit()
        db.refresh(nuevo_pedido)
        return nuevo_pedido

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en la transacción del pedido: {str(e)}"
        )
