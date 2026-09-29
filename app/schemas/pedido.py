from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel, Field, model_validator


class ItemIn(BaseModel):
    """Acepta producto_id, id o product_id indistintamente."""
    producto_id: Optional[int] = None
    id: Optional[int] = None
    product_id: Optional[int] = None
    cantidad: int = Field(..., gt=0, description="La cantidad debe ser mayor a 0")

    @model_validator(mode="after")
    def resolver_producto_id(self) -> "ItemIn":
        # Normalizar: toma el primer valor no nulo entre las variantes
        pid = self.producto_id or self.id or self.product_id
        if pid is None:
            raise ValueError("Se requiere producto_id, id o product_id")
        self.producto_id = pid
        return self


class PedidoCreate(BaseModel):
    """
    Acepta cualquiera de estas formas:
      - { "items": [...] }
      - { "productos": [...] }
      - array directo [...] — manejado en el endpoint via Request
    """
    items: List[ItemIn] = []
    productos: Optional[List[ItemIn]] = None
    # Campos opcionales que el frontend podría enviar
    direccion: Optional[str] = None
    metodo_pago: Optional[str] = None
    notas: Optional[str] = None

    @model_validator(mode="after")
    def unificar_items(self) -> "PedidoCreate":
        # Si llegaron en "productos" y no en "items", moverlos
        if not self.items and self.productos:
            self.items = self.productos
        return self


class ItemOut(BaseModel):
    id: int
    producto_id: int
    cantidad: int
    precio_unitario: float
    producto_nombre: Optional[str] = None

    class Config:
        from_attributes = True


# Alias for backwards compatibility
ItemPedidoOut = ItemOut
ItemCart = ItemIn


class PedidoOut(BaseModel):
    id: int
    usuario_id: int
    estado: str
    total: float
    fecha_creacion: datetime
    codigo_solicitud_revocacion: Optional[str] = None
    items: List[ItemOut] = []

    class Config:
        from_attributes = True


class SolicitudArrepentimientoPublicaIn(BaseModel):
    pedido_id: int
    email: str
