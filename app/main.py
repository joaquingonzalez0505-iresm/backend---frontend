from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship

# 1. BASE DE DATOS SQLITE (Genera el archivo stickerlab.db para DBeaver)
SQLALCHEMY_DATABASE_URL = "sqlite:///./stickerlab.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ==================== TABLAS PARA DBEAVER ====================
class UsuarioModel(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    es_admin = Column(Boolean, default=False)
    token = Column(String, nullable=True)

class ProductoModel(Base):
    __tablename__ = "productos"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    descripcion = Column(String, nullable=False)
    precio_final = Column(Float, nullable=False)
    cuotas_cantidad = Column(Integer, default=3)
    stock = Column(Integer, default=50)
    imagen_url = Column(String, nullable=True)

class PedidoModel(Base):
    __tablename__ = "pedidos"
    id = Column(Integer, primary_key=True, index=True)
    nombre_cliente = Column(String, nullable=False)
    total = Column(Float, nullable=False)
    estado = Column(String, default="Pendiente")
    items = relationship("ItemPedidoModel", back_populates="pedido")

class ItemPedidoModel(Base):
    __tablename__ = "item_pedidos"
    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"))
    nombre = Column(String, nullable=False)
    precio_final = Column(Float, nullable=False)
    cantidad = Column(Integer, nullable=False)
    pedido = relationship("PedidoModel", back_populates="items")

Base.metadata.create_all(bind=engine)

# ==================== APLICACIÓN FASTAPI ====================
app = FastAPI(
    title="IRESM StickerLab API",
    description="API con SQLite persistente para DBeaver y panel de Admin",
    version="3.0.0"
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Cargar Datos Iniciales si la DB está vacía
@app.on_event("startup")
def startup_db_seed():
    db = SessionLocal()
    if not db.query(UsuarioModel).filter_by(email="joaquin@iresm.edu.ar").first():
        admin_user = UsuarioModel(
            nombre="Joaquín",
            email="joaquin@iresm.edu.ar",
            password="123",
            es_admin=True,
            token="token_admin_joaquin"
        )
        db.add(admin_user)

    if db.query(ProductoModel).count() == 0:
        productos_defecto = [
            ProductoModel(
                nombre="Pack Stickers Developer & Code",
                descripcion="Set de 10 stickers en vinilo de Python, React, JS y Docker.",
                precio_final=3500.0,
                stock=50,
                imagen_url="https://images.unsplash.com/photo-1572375992501-4b0892d50c69?w=500"
            ),
            ProductoModel(
                nombre="Sticker Holográfico Cyberpunk",
                descripcion="Vinilo holográfico brillante impermeable.",
                precio_final=1200.0,
                stock=100,
                imagen_url="https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=500"
            )
        ]
        db.add_all(productos_defecto)
    db.commit()
    db.close()

# ==================== ESQUEMAS PYDANTIC ====================
class UsuarioRegister(BaseModel):
    nombre: str
    email: str
    password: str

class UsuarioLogin(BaseModel):
    email: str
    password: str

class ProductoCreate(BaseModel):
    nombre: str
    descripcion: str
    precio_final: float
    cuotas_cantidad: int = 3
    stock: int = 50
    imagen_url: Optional[str] = None

class ItemPedidoSchema(BaseModel):
    nombre: str
    precio_final: float
    cantidad: int

class PedidoRequest(BaseModel):
    nombre_cliente: str
    items: List[ItemPedidoSchema]
    total: float

# ==================== AUTENTICACIÓN ====================
def obtener_usuario_actual(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    usuario = db.query(UsuarioModel).filter(UsuarioModel.token == token).first()
    if not usuario:
        raise HTTPException(status_code=401, detail="Token o credenciales inválidas")
    return usuario

@app.post("/token", tags=["Autenticación"])
def login_swagger(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    u = db.query(UsuarioModel).filter(UsuarioModel.email == form_data.username).first()
    if u and u.password == form_data.password:
        return {"access_token": u.token, "token_type": "bearer"}
    raise HTTPException(status_code=400, detail="Credenciales incorrectas")

@app.post("/auth/register", tags=["Autenticación"])
def registrar_usuario(usuario: UsuarioRegister, db: Session = Depends(get_db)):
    existente = db.query(UsuarioModel).filter(UsuarioModel.email == usuario.email).first()
    if existente:
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    
    nuevo_u = UsuarioModel(
        nombre=usuario.nombre,
        email=usuario.email,
        password=usuario.password,
        es_admin=False,
        token=f"token_user_{usuario.email}"
    )
    db.add(nuevo_u)
    db.commit()
    db.refresh(nuevo_u)
    return {"id": nuevo_u.id, "nombre": nuevo_u.nombre, "email": nuevo_u.email, "es_admin": nuevo_u.es_admin}

@app.post("/auth/login", tags=["Autenticación"])
def login(credenciales: UsuarioLogin, db: Session = Depends(get_db)):
    u = db.query(UsuarioModel).filter(UsuarioModel.email == credenciales.email).first()
    if u and u.password == credenciales.password:
        return {
            "access_token": u.token,
            "user": {
                "id": u.id,
                "nombre": u.nombre,
                "email": u.email,
                "es_admin": u.es_admin
            }
        }
    raise HTTPException(status_code=401, detail="Email o contraseña incorrectos")

@app.put("/usuarios/hacer-admin/{email}", tags=["Usuarios"])
def hacer_admin(email: str, db: Session = Depends(get_db)):
    u = db.query(UsuarioModel).filter(UsuarioModel.email == email).first()
    if not u:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    u.es_admin = True
    db.commit()
    return {"message": f"El usuario {u.nombre} ({u.email}) ahora es Administrador"}

# ==================== PRODUCTOS ====================
@app.get("/productos/", tags=["Productos"])
def obtener_productos(db: Session = Depends(get_db)):
    return db.query(ProductoModel).all()

@app.post("/productos/", status_code=201, tags=["Productos"])
def crear_producto(
    prod: ProductoCreate, 
    db: Session = Depends(get_db),
    usuario_actual: UsuarioModel = Depends(obtener_usuario_actual)  # Requiere token para habilitar Authorize
):
    nuevo_p = ProductoModel(**prod.dict())
    db.add(nuevo_p)
    db.commit()
    db.refresh(nuevo_p)
    return nuevo_p

# ==================== PEDIDOS ====================
@app.post("/pedidos/", status_code=201, tags=["Pedidos"])
def crear_pedido(ped: PedidoRequest, db: Session = Depends(get_db)):
    nuevo_pedido = PedidoModel(nombre_cliente=ped.nombre_cliente, total=ped.total, estado="Pendiente")
    db.add(nuevo_pedido)
    db.commit()
    db.refresh(nuevo_pedido)

    for item in ped.items:
        db_item = ItemPedidoModel(
            pedido_id=nuevo_pedido.id,
            nombre=item.nombre,
            precio_final=item.precio_final,
            cantidad=item.cantidad
        )
        db.add(db_item)
    
    db.commit()
    return {"message": "Pedido guardado con éxito", "id": nuevo_pedido.id}

@app.get("/pedidos/", tags=["Pedidos"])
def obtener_pedidos(db: Session = Depends(get_db)):
    return db.query(PedidoModel).all()