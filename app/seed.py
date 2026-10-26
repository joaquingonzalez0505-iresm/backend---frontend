"""
app/seed.py
───────────
Script de inicialización (seed) para la base de datos de producción o desarrollo.
- Lee las variables de entorno: DATABASE_URL, SEED_ADMIN_EMAIL y SEED_ADMIN_PASSWORD.
- Es IDEMPOTENTE: verifica si el administrador o los productos ya existen antes de insertarlos.
- Configura las imágenes de los productos apuntando a la ruta estática '/demo/'.
"""

import os
import sys
from datetime import datetime, timezone

# Asegurar que el directorio raíz del proyecto esté en sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker

# Intentar importar la función de hashing de seguridad
try:
    from app.core.security import get_password_hash
except Exception:
    import bcrypt

    def get_password_hash(password: str) -> str:
        pwd_bytes = password.encode("utf-8")[:72]
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


# ── Catálogo de productos de demostración para producción ────────────────────
# Todas las imágenes apuntan al endpoint estático /demo/
DEMO_PRODUCTOS = [
    {
        "nombre": "Pack Stickers Developer & Code",
        "descripcion": "Set de 10 stickers en vinilo de alta resistencia: Python, FastAPI, Docker, React y Linux.",
        "precio_final": 3500.0,
        "cuotas_cantidad": 3,
        "cuotas_valor": 1166.67,
        "garantia_meses": 6,
        "stock": 50,
        "imagen": "/demo/sticker-dev.svg",
        "imagen_url": "/demo/sticker-dev.svg",
    },
    {
        "nombre": "Sticker Holográfico Cyberpunk",
        "descripcion": "Sticker vinilo holográfico brillante impermeable tornasolado especial para notebooks.",
        "precio_final": 1200.0,
        "cuotas_cantidad": 3,
        "cuotas_valor": 400.0,
        "garantia_meses": 6,
        "stock": 100,
        "imagen": "/demo/sticker-cyberpunk.svg",
        "imagen_url": "/demo/sticker-cyberpunk.svg",
    },
    {
        "nombre": "Notebook Gamer Asus ROG Strix G16",
        "descripcion": "Notebook potente para desarrollo de software y gaming de alta gama.",
        "precio_final": 1450000.0,
        "cuotas_cantidad": 12,
        "cuotas_valor": 120833.33,
        "garantia_meses": 24,
        "stock": 8,
        "imagen": "/demo/notebook-gamer.svg",
        "imagen_url": "/demo/notebook-gamer.svg",
    },
    {
        "nombre": "Monitor Gamer LG UltraGear 27\" 144Hz",
        "descripcion": "Monitor IPS Full HD 144Hz con 1ms de respuesta y FreeSync Premium.",
        "precio_final": 380000.0,
        "cuotas_cantidad": 6,
        "cuotas_valor": 63333.33,
        "garantia_meses": 12,
        "stock": 12,
        "imagen": "/demo/notebook-gamer.svg",
        "imagen_url": "/demo/notebook-gamer.svg",
    },
    {
        "nombre": "Teclado Mecánico RGB Redragon Kumara",
        "descripcion": "Teclado mecánico switches Outemu Blue, iluminación RGB y chasis reforzado.",
        "precio_final": 65000.0,
        "cuotas_cantidad": 3,
        "cuotas_valor": 21666.67,
        "garantia_meses": 12,
        "stock": 25,
        "imagen": "/demo/teclado-mecanico.svg",
        "imagen_url": "/demo/teclado-mecanico.svg",
    },
    {
        "nombre": "Mouse Inalámbrico Logitech G Pro X",
        "descripcion": "Mouse ultraligero para eSports con sensor HERO 25K de máxima precisión.",
        "precio_final": 120000.0,
        "cuotas_cantidad": 3,
        "cuotas_valor": 40000.0,
        "garantia_meses": 12,
        "stock": 20,
        "imagen": "/demo/mouse-inalambrico.svg",
        "imagen_url": "/demo/mouse-inalambrico.svg",
    },
    {
        "nombre": "Auriculares Gamer HyperX Cloud II",
        "descripcion": "Auriculares profesionales con sonido envolvente 7.1 y micrófono con cancelación de ruido.",
        "precio_final": 95000.0,
        "cuotas_cantidad": 3,
        "cuotas_valor": 31666.67,
        "garantia_meses": 12,
        "stock": 15,
        "imagen": "/demo/auriculares-gamer.svg",
        "imagen_url": "/demo/auriculares-gamer.svg",
    },
]


def seed():
    # ── 1. Lectura de Variables de Entorno ──────────────────────────────────────
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        try:
            from app.core.config import settings
            db_url = settings.DATABASE_URL
        except Exception:
            db_url = "sqlite:///./sql_app.db"

    # Compatibilidad con proveedores de hosting que exportan 'postgres://'
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    admin_email = os.getenv("SEED_ADMIN_EMAIL", "admin@stickerlab.com")
    admin_password = os.getenv("SEED_ADMIN_PASSWORD", "Admin1234!")

    print("=" * 65)
    print("  SEED PRODUCCIÓN — Inicialización Idempotente")
    print("=" * 65)
    print(f"[CONFIG] DB URL: {db_url.split('@')[-1] if '@' in db_url else db_url}")
    print(f"[CONFIG] Admin Email: {admin_email}")

    # ── 2. Creación de Engine y Verificación de Tablas ─────────────────────────
    connect_args = {"check_same_thread": False} if db_url.startswith("sqlite") else {}
    engine = create_engine(db_url, connect_args=connect_args)

    # Asegurar creación de tablas si aún no han sido migradas
    try:
        from app.database import Base
        import app.models
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"[AVISO] Creación de metadata omitida/existente: {e}")

    inspector = inspect(engine)
    tablas = inspector.get_table_names()

    if "usuarios" not in tablas or "productos" not in tablas:
        print("[ERROR] Las tablas 'usuarios' o 'productos' no existen en la base de datos.")
        return

    cols_usuario = {col["name"] for col in inspector.get_columns("usuarios")}
    cols_producto = {col["name"] for col in inspector.get_columns("productos")}

    with engine.connect() as conn:
        trans = conn.begin()
        try:
            # ── 3. Seed Administrador (Idempotente) ──────────────────────────────
            print("\n[SEED] Verificando usuario administrador...")
            check_admin = conn.execute(
                text("SELECT id, email FROM usuarios WHERE email = :email"),
                {"email": admin_email}
            ).first()

            if check_admin:
                print(f"  [OMITIDO] El usuario administrador '{admin_email}' ya existe (id={check_admin[0]}).")
            else:
                admin_dict = {
                    "email": admin_email,
                    "nombre": "Administrador Demo",
                }
                if "hashed_password" in cols_usuario:
                    admin_dict["hashed_password"] = get_password_hash(admin_password)
                if "password" in cols_usuario:
                    admin_dict["password"] = admin_password
                if "rol" in cols_usuario:
                    admin_dict["rol"] = "admin"
                if "es_admin" in cols_usuario:
                    admin_dict["es_admin"] = True
                if "token" in cols_usuario:
                    admin_dict["token"] = f"token_admin_{admin_email}"
                if "activo" in cols_usuario:
                    admin_dict["activo"] = True
                if "acepto_tratamiento" in cols_usuario:
                    admin_dict["acepto_tratamiento"] = True
                if "fecha_consentimiento" in cols_usuario:
                    admin_dict["fecha_consentimiento"] = datetime.now(timezone.utc)

                cols_insert = [c for c in admin_dict.keys() if c in cols_usuario]
                cols_str = ", ".join(cols_insert)
                vals_str = ", ".join(f":{c}" for c in cols_insert)
                query_admin = text(f"INSERT INTO usuarios ({cols_str}) VALUES ({vals_str})")
                conn.execute(query_admin, {c: admin_dict[c] for c in cols_insert})
                print(f"  [INSERTADO] Administrador '{admin_email}' creado exitosamente.")

            # ── 4. Seed Productos (Idempotente) ─────────────────────────────────
            print("\n[SEED] Verificando productos de demostración...")
            insertados = 0
            omitidos = 0

            for prod in DEMO_PRODUCTOS:
                check_prod = conn.execute(
                    text("SELECT id, nombre FROM productos WHERE nombre = :nombre"),
                    {"nombre": prod["nombre"]}
                ).first()

                if check_prod:
                    print(f"  [OMITIDO] Producto '{prod['nombre']}' ya existe (id={check_prod[0]}).")
                    omitidos += 1
                else:
                    prod_dict = {}
                    for col in cols_producto:
                        if col in prod:
                            prod_dict[col] = prod[col]

                    if "precio_final" in cols_producto and "precio_final" not in prod_dict:
                        prod_dict["precio_final"] = prod.get("precio_final", 1000.0)
                    if "precio" in cols_producto and "precio" not in prod_dict:
                        prod_dict["precio"] = prod.get("precio_final", 1000.0)
                    if "stock" in cols_producto and "stock" not in prod_dict:
                        prod_dict["stock"] = prod.get("stock", 10)

                    cols_p = [c for c in prod_dict.keys() if c in cols_producto]
                    cols_str = ", ".join(cols_p)
                    vals_str = ", ".join(f":{c}" for c in cols_p)
                    query_prod = text(f"INSERT INTO productos ({cols_str}) VALUES ({vals_str})")
                    conn.execute(query_prod, {c: prod_dict[c] for c in cols_p})
                    print(f"  [INSERTADO] '{prod['nombre']}' -> img: {prod.get('imagen_url') or prod.get('imagen')}")
                    insertados += 1

            trans.commit()
            print("\n" + "=" * 65)
            print(f"[EXITO] Seed finalizado. Insertados: {insertados} | Omitidos: {omitidos}")
            print("=" * 65)

        except Exception as e:
            trans.rollback()
            print(f"\n[ERROR] Falló la ejecución del seed: {e}")
            raise


if __name__ == "__main__":
    seed()
