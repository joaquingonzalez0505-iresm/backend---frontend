def test_registro_sin_consentimiento_se_rechaza(client):
    r = client.post(
        "/auth/register",
        json={
            "nombre": "Sin Consentimiento",
            "email": "sincon@prueba.com",
            "password": "clave-larga-123",
            "acepto_tratamiento": False,
        },
    )
    assert r.status_code == 422


def test_registro_con_consentimiento_y_login(client):
    r = client.post(
        "/auth/register",
        json={
            "nombre": "Con Consentimiento",
            "email": "concon@prueba.com",
            "password": "clave-larga-123",
            "acepto_tratamiento": True,
        },
    )
    assert r.status_code in (200, 201)
    assert "password" not in r.json()

    login_r = client.post(
        "/auth/login",
        data={"username": "concon@prueba.com", "password": "clave-larga-123"},
    )
    assert login_r.status_code == 200


def test_login_con_clave_incorrecta(client):
    r = client.post(
        "/auth/login",
        data={"username": "nadie@prueba.com", "password": "clave-erronea"},
    )
    assert r.status_code in (400, 401)