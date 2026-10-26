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

app = FastAPI(title=settings.PROJECT_NAME, version="3.0.0", redirect_slashes=False)

# Configuración CORS universal para aceptar peticiones desde Vercel y clientes locales
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="uploads"), name="static")
app.mount("/demo", StaticFiles(directory="app/static/demo"), name="demo")

@app.get("/")
@app.head("/")
def root():
    return {"mensaje": "API StickerLab activa", "version": "3.0.0"}

app.include_router(auth.router)
app.include_router(productos.router)
app.include_router(pedidos.router)
app.include_router(usuarios.router)


@app.on_event("startup")
def startup_setup():
    # 1. Asegurar columnas y restricciones en SQLite
    try:
        from sqlalchemy import inspect as sa_inspect, text
        if str(engine.url).startswith("sqlite"):
            inspector = sa_inspect(engine)
            if "productos" in inspector.get_table_names():
                cols = {c["name"] for c in inspector.get_columns("productos")}
                with engine.connect() as conn:
                    if "descripcion" not in cols:
                        conn.execute(text("ALTER TABLE productos ADD COLUMN descripcion VARCHAR DEFAULT ''"))
                    if "precio" not in cols:
                        conn.execute(text("ALTER TABLE productos ADD COLUMN precio FLOAT DEFAULT 0.0"))
                    conn.commit()
    except Exception as e:
        print(f"--> [DB-INIT] Info columnas SQLite: {e}")

    # 2. Asegurar Super Admin Joaquin
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
                rol="admin",
                activo=True,
                acepto_tratamiento=True
            )
            db.add(usuario)
        else:
            usuario.hashed_password = hash_password("123")
            usuario.rol = "admin"
            usuario.activo = True
            usuario.acepto_tratamiento = True

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
                rol="admin",
                activo=True,
                acepto_tratamiento=True
            )
            db.add(usuario)
        else:
            usuario.hashed_password = hash_password("123")
            usuario.rol = "admin"
            usuario.activo = True
            usuario.acepto_tratamiento = True

        db.commit()
        db.close()
        return {"status": "EXITO", "mensaje": "Super Admin restaurado con clave 123"}
    except Exception as e:
        return {"status": "ERROR", "detalle": str(e)}