import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from starlette.testclient import TestClient
from app.main import app

from app.database import SessionLocal
from app.models import Producto, Usuario
from app.core.security import hash_password

client = TestClient(app)

def setup_module(module):
    """Ensure database has the super admin and test products."""
    db = SessionLocal()
    # Ensure Joaquin exists
    admin = db.query(Usuario).filter(Usuario.email == "joaquin@iresm.edu.ar").first()
    if not admin:
        admin = Usuario(
            email="joaquin@iresm.edu.ar",
            nombre="Joaquin Admin",
            hashed_password=hash_password("123"),
            rol="admin",
            activo=True,
            acepto_tratamiento=True
        )
        db.add(admin)
        db.commit()
    db.close()

# ─────────────────────────────────────────────────────────────
# 1. Tests for Product Endpoints & Database Constraints
# ─────────────────────────────────────────────────────────────

def test_crear_producto_solo_con_precio():
    """Validates that sending only 'precio' sets both 'precio' and 'precio_final' without IntegrityError."""
    payload = {
        "nombre": "Sticker Test Produccion",
        "precio": 2500.50,
        "stock": 15
    }
    response = client.post("/productos", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["nombre"] == "Sticker Test Produccion"
    assert data["precio"] == 2500.50
    assert data["precio_final"] == 2500.50
    assert data["cuotas_cantidad"] == 1
    assert data["cuotas"] == 1
    assert data["cuotas_valor"] == 2500.50
    assert data["garantia_meses"] == 0
    assert data["imagen"] == ""
    assert data["imagen_url"] == ""

def test_crear_producto_con_cuotas_y_url():
    """Validates that cuotas and image URL are mapped properly with valid defaults."""
    payload = {
        "title": "Sticker Gamer Holo",
        "price": 6000,
        "cuotas": 3,
        "image": "https://example.com/sticker.png"
    }
    response = client.post("/productos/", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["nombre"] == "Sticker Gamer Holo"
    assert data["precio"] == 6000.0
    assert data["precio_final"] == 6000.0
    assert data["cuotas_cantidad"] == 3
    assert data["cuotas"] == 3
    assert data["cuotas_valor"] == 2000.0
    assert "example.com" in data["imagen_url"]

def test_actualizar_producto():
    """Validates PUT endpoint maps dynamic fields and updates both precio and precio_final."""
    # First create
    p_res = client.post("/productos", json={"nombre": "Para Actualizar", "precio": 1000})
    assert p_res.status_code == 200
    prod_id = p_res.json()["id"]

    # Now update with PUT
    put_res = client.put(f"/productos/{prod_id}", json={
        "nombre": "Actualizado OK",
        "precio": 4500,
        "cuotas": 6
    })
    assert put_res.status_code == 200, put_res.text
    data = put_res.json()
    assert data["nombre"] == "Actualizado OK"
    assert data["precio"] == 4500.0
    assert data["precio_final"] == 4500.0
    assert data["cuotas_cantidad"] == 6

def test_listar_y_obtener_productos():
    """Validates GET endpoints without trailing slash and with trailing slash."""
    r1 = client.get("/productos")
    assert r1.status_code == 200
    assert isinstance(r1.json(), list)
    assert len(r1.json()) > 0

    r2 = client.get("/productos/")
    assert r2.status_code == 200
    assert isinstance(r2.json(), list)

    first_id = r1.json()[0]["id"]
    r_item = client.get(f"/productos/{first_id}")
    assert r_item.status_code == 200
    assert r_item.json()["id"] == first_id

# ─────────────────────────────────────────────────────────────
# 2. Tests for Authentication, Admin Role & Enriched Responses
# ─────────────────────────────────────────────────────────────

def test_login_joaquin_admin_structure():
    """Validates login response structure and admin role for joaquin@iresm.edu.ar."""
    payload = {
        "email": "joaquin@iresm.edu.ar",
        "password": "123"
    }
    response = client.post("/auth/login", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()

    # Required top-level fields
    assert "access_token" in data
    assert "token" in data
    assert data["token_type"] == "bearer"
    assert data["rol"] == "admin"
    assert data["is_admin"] is True

    # Required user object
    user = data["user"]
    assert user["email"] == "joaquin@iresm.edu.ar"
    assert user["rol"] == "admin"
    assert user["role"] == "admin"
    assert user["es_admin"] is True
    assert user["is_admin"] is True
    assert user["isAdmin"] is True

    # Required usuario object (identical to user)
    usuario = data["usuario"]
    assert usuario == user

def test_auth_me_enriched_response():
    """Validates GET /auth/me returns enriched response with admin credentials."""
    login_res = client.post("/auth/login", json={"email": "joaquin@iresm.edu.ar", "password": "123"})
    token = login_res.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    r = client.get("/auth/me", headers=headers)
    assert r.status_code == 200, r.text
    data = r.json()

    assert data["email"] == "joaquin@iresm.edu.ar"
    assert data["rol"] == "admin"
    assert data["role"] == "admin"
    assert data["es_admin"] is True
    assert data["is_admin"] is True
    assert data["isAdmin"] is True
    assert "user" in data
    assert "usuario" in data
    assert data["user"]["rol"] == "admin"
    assert data["usuario"]["is_admin"] is True

def test_usuarios_me_enriched_response():
    """Validates GET /usuarios/me returns enriched response with admin credentials."""
    login_res = client.post("/auth/login", json={"email": "joaquin@iresm.edu.ar", "password": "123"})
    token = login_res.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    r = client.get("/usuarios/me", headers=headers)
    assert r.status_code == 200, r.text
    data = r.json()

    assert data["email"] == "joaquin@iresm.edu.ar"
    assert data["rol"] == "admin"
    assert data["role"] == "admin"
    assert data["es_admin"] is True
    assert data["is_admin"] is True
    assert data["isAdmin"] is True
    assert "user" in data
    assert "usuario" in data
    assert data["user"]["rol"] == "admin"
    assert data["usuario"]["is_admin"] is True

# ─────────────────────────────────────────────────────────────
# 3. Tests for CORS & Redirect Slashes
# ─────────────────────────────────────────────────────────────

def test_cors_headers():
    """Validates CORSMiddleware with credentials=True and allow_origins=* reflects origin."""
    origin = "https://frontend-lugani.vercel.app"
    response = client.get("/", headers={"Origin": origin})
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == origin
    assert response.headers.get("access-control-allow-credentials") == "true"

def test_cors_preflight():
    """Validates CORS preflight OPTIONS request."""
    origin = "http://localhost:5173"
    response = client.options("/productos", headers={
        "Origin": origin,
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "content-type"
    })
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == origin
    assert response.headers.get("access-control-allow-credentials") == "true"

def test_fix_admin_endpoint():
    """Validates /fix-admin resets super admin correctly."""
    res = client.get("/fix-admin")
    assert res.status_code == 200
    assert res.json()["status"] == "EXITO"

def test_no_trailing_slash_redirects():
    """Validates that routes work directly with or without trailing slash without 307 redirect."""
    r1 = client.get("/productos")
    assert r1.status_code == 200
    r2 = client.get("/productos/")
    assert r2.status_code == 200

