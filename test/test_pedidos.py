from .ayudantes import cuerpo_pedido

def test_compra_descuenta_stock(client, cliente, producto):
    r = client.post(
        "/pedidos", headers=cliente, json=cuerpo_pedido(producto["id"], 1)
    )
    assert r.status_code in (200, 201)
    prod = client.get(f"/productos/{producto['id']}").json()
    assert prod["stock"] == 1


def test_sin_stock_da_409_y_no_toca_nada(client, cliente, producto):
    r = client.post(
        "/pedidos", headers=cliente, json=cuerpo_pedido(producto["id"], 5)
    )
    assert r.status_code in (400, 409)
    assert client.get(f"/productos/{producto['id']}").json()["stock"] == 2


def test_comprar_sin_sesion_da_401(client, producto):
    r = client.post("/pedidos", json=cuerpo_pedido(producto["id"], 1))
    assert r.status_code == 401