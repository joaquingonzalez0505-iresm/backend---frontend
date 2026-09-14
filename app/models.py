# pyrefly: ignore [missing-import]
from sqlalchemy import Column, Integer, String, Float, ForeignKey
# pyrefly: ignore [missing-import]
from .database import Base

class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    precio_final = Column(Float, nullable=False)
    cuotas_cantidad = Column(Integer, nullable=False)
    cuotas_valor = Column(Float, nullable=False)
    garantia_meses = Column(Integer, nullable=False)
    stock = Column(Integer, nullable=False)

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    rol = Column(String, nullable=False, default="cliente")

class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    estado = Column(String, nullable=False, default="pendiente")
    total = Column(Float, nullable=False)

class ItemPedido(Base):
    __tablename__ = "item_pedidos"

    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"), nullable=False)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Float, nullable=False)