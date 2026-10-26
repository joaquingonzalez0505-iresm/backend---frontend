from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.database import engine, Base, SessionLocal
from app.routers import auth, productos, pedidos, usuarios

Base.metadata.create_all(bind=engine)

Path("uploads/productos").mkdir(parents=True, exist_ok=True)
Path("app/static/demo").mkdir(parents=True, exist_ok=True)

# Desactivar redirección automática de barra final para evitar que la redirección elimine encabezados CORS
app = FastAPI(
    title=settings.PROJECT_NAME, 
    version="3.0.0",
    redirect_slashes=False
)

# Permitir explícitamente tu dominio en Vercel y orígenes locales
origins = [
    "https://frontend-lugani-3spl.vercel.app",
    "http://localhost:3000",
    "http://localhost:5173",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="uploads"), name="static")
app.mount("/demo", StaticFiles(directory="app/static/demo"), name="demo")

@app.get("/")
def root():
    return {"mensaje": "API StickerLab activa", "version": "3.0.0"}

app.include_router(auth.router)
app.include_router(productos.router)
app.include_router(pedidos.router)
app.include_router(usuarios.router)


@app.on_event("startup")
def forzar_super_admin():
    try:
        from app.models import Usuario
        from app.core.security import hash_password
        db = SessionLocal()
        email_target = "joaquin@iresm.edu.ar"
        usuario = db.query(Usuario).filter(Usuario.email == email_target).first()

        if not usuario:
            usuario = Usuario(
                email=email_target,
                nombre="Joaquin Admin",
                hashed_password=hash_password("123"),
                rol="admin"
            )
            db.add(usuario)
        else:
            usuario.hashed_password = hash_password("123")
            usuario.rol = "admin"

        db.commit()
        db.close()
        print("--> [ADMIN] Super Admin Joaquin (pass: 123) listo en la base de datos.")
    except Exception as e:
        print(f"--> [ADMIN] Error en startup: {e}")


@app.get("/fix-admin")
def fix_admin_endpoint():
    try:
        from app.models import Usuario
        from app.core.security import hash_password
        db = SessionLocal()
        email_target = "joaquin@iresm.edu.ar"
        usuario = db.query(Usuario).filter(Usuario.email == email_target).first()

        if not usuario:
            usuario = Usuario(
                email=email_target,
                nombre="Joaquin Admin",
                hashed_password=hash_password("123"),
                rol="admin"
            )
            db.add(usuario)
        else:
            usuario.hashed_password = hash_password("123")
            usuario.rol = "admin"

        db.commit()
        db.close()
        return {"status": "EXITO", "mensaje": "Super Admin restaurado con clave 123"}
    except Exception as e:
        return {"status": "ERROR", "detalle": str(e)}