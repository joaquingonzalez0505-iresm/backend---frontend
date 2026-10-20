from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.database import engine, Base, SessionLocal
from app.routers import auth, productos, pedidos, usuarios

# Crear tablas desde app.models
Base.metadata.create_all(bind=engine)

# Asegurar directorios de uploads y demo
Path("uploads/productos").mkdir(parents=True, exist_ok=True)
Path("app/static/demo").mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="3.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="uploads"), name="static")
app.mount("/demo", StaticFiles(directory="app/static/demo"), name="demo")

# Ruta raíz simple para evitar duplicaciones
@app.get("/")
def root():
    return {"mensaje": "API StickerLab activa", "version": "3.0.0"}

# Incluir Routers Modulares
app.include_router(auth.router)
app.include_router(productos.router)
app.include_router(pedidos.router)
app.include_router(usuarios.router)


# --- AUTOMATIZACIÓN DE USUARIO ADMIN ---

@app.on_event("startup")
def asegurar_admin():
    """Al iniciar el servidor, si existe joaquin@iresm.edu.ar le otorga rol de Admin."""
    try:
        from app.models import Usuario
        db = SessionLocal()
        email_target = "joaquin@iresm.edu.ar"
        usuario = db.query(Usuario).filter(Usuario.email == email_target).first()

        if usuario:
            if hasattr(usuario, "rol"):
                usuario.rol = "admin"
            if hasattr(usuario, "es_admin"):
                usuario.es_admin = True
            if hasattr(usuario, "is_admin"):
                usuario.is_admin = True
            db.commit()
            print(f"--> [ADMIN] Usuario {email_target} verificado como ADMIN.")
        db.close()
    except Exception as e:
        print(f"--> [ADMIN] Error en startup: {e}")


@app.get("/fix-admin")
def fix_admin_endpoint():
    """Endpoint de verificación manual de administrador."""
    try:
        from app.models import Usuario
        db = SessionLocal()
        email_target = "joaquin@iresm.edu.ar"
        usuario = db.query(Usuario).filter(Usuario.email == email_target).first()

        if not usuario:
            db.close()
            return {
                "status": "NO_EXISTE",
                "mensaje": f"El usuario {email_target} aún no existe en la base de datos de Render. Regístrate en el Frontend y luego vuelve a cargar esta URL."
            }

        if hasattr(usuario, "rol"):
            usuario.rol = "admin"
        if hasattr(usuario, "es_admin"):
            usuario.es_admin = True
        if hasattr(usuario, "is_admin"):
            usuario.is_admin = True

        db.commit()
        db.close()

        return {
            "status": "EXITO",
            "mensaje": f"¡Listo! {email_target} ahora es ADMINISTRADOR. Cierra sesión en el Frontend y vuelve a ingresar."
        }
    except Exception as e:
        return {"status": "ERROR", "detalle": str(e)}