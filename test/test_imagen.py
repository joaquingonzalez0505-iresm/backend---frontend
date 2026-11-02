TRAMPA = ("foto.png", b"esto es texto con nombre de imagen", "image/png")


def test_archivo_trampa_da_415(client, admin, producto):
    r = client.post(
        f"/productos/{producto['id']}/imagen",
        headers=admin,
        files={"archivo": TRAMPA},
    )
    assert r.status_code in (400, 415)


def test_cliente_no_puede_subir_imagen(client, cliente, producto):
    r = client.post(
        f"/productos/{producto['id']}/imagen",
        headers=cliente,
        files={"archivo": TRAMPA},
    )
    assert r.status_code in (401, 403)


def test_sin_sesion_no_puede_subir_imagen(client, producto):
    r = client.post(
        f"/productos/{producto['id']}/imagen",
        files={"archivo": TRAMPA},
    )
    assert r.status_code == 401