def test_arrepentimiento_sin_sesion(client):
    r = client.post(
        "/arrepentimiento",
        json={"email": "cliente@prueba.com", "pedido_id": 1},
    )
    assert r.status_code in (200, 201)
    assert "codigo" in r.json()


def test_arrepentimiento_no_revela(client):
    r = client.post(
        "/arrepentimiento",
        json={"email": "cliente@prueba.com", "pedido_id": 99999},
    )
    assert r.status_code in (200, 201)
    assert "codigo" in r.json()