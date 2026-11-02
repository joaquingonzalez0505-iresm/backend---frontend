"""Funciones auxiliares reutilizables para las pruebas del backend."""

def registrar(client, email="cliente@prueba.com", password="clave-larga-123"):
    r = client.post(
        "/auth/register",
        json={
            "nombre": "Cliente de Prueba",
            "email": email,
            "password": password,
            "acepto_tratamiento": True,
        },
    )
    assert r.status_code in (200, 201), r.text
    return email, password


def token_de(client, email, password):
    r = client.post("/auth/login", data={"username": email, "password": password})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def cuerpo_pedido(producto_id, cantidad):
    return {"items": [{"producto_id": producto_id, "cantidad": cantidad}]}