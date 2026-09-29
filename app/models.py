from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, DateTime, Numeric
from sqlalchemy.orm import relationship
from .database import Base

class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    precio_final = Column(Float, nullable=False)
    cuotas_cantidad = Column(Integer, nullable=False, default=1)
    cuotas_valor = Column(Float, nullable=False, default=0.0)
    garantia_meses = Column(Integer, nullable=False, default=0)
    stock = Column(Integer, nullable=False, default=0)
    imagen = Column(String, nullable=True)
    imagen_url = Column(String, nullable=True)

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    rol = Column(String, nullable=False, default="customer")
    acepto_tratamiento = Column(Boolean, nullable=False, default=False)
    fecha_consentimiento = Column(DateTime, nullable=True)
    activo = Column(Boolean, nullable=False, default=True)
    fecha_baja = Column(DateTime, nullable=True)

    pedidos = relationship("Pedido", back_populates="usuario", cascade="all, delete-orphan")
    solicitudes_revocacion = relationship("SolicitudRevocacion", back_populates="usuario")

class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    estado = Column(String, nullable=False, default="pendiente")
    total = Column(Numeric(12, 2), nullable=False)
    fecha_creacion = Column(DateTime, nullable=False, default=datetime.utcnow)

    usuario = relationship("Usuario", back_populates="pedidos")
    items = relationship("ItemPedido", back_populates="pedido", cascade="all, delete-orphan")
    solicitud_revocacion = relationship("SolicitudRevocacion", back_populates="pedido", uselist=False)

class ItemPedido(Base):
    __tablename__ = "item_pedidos"

    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"), nullable=False)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Numeric(12, 2), nullable=False)

    pedido = relationship("Pedido", back_populates="items")
    producto = relationship("Producto")

class SolicitudRevocacion(Base):
    __tablename__ = "solicitudes_revocacion"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String, unique=True, nullable=False, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    creada_en = Column(DateTime, nullable=False, default=datetime.utcnow)

    usuario = relationship("Usuario", back_populates="solicitudes_revocacion")
    pedido = relationship("Pedido", back_populates="solicitud_revocacion")

