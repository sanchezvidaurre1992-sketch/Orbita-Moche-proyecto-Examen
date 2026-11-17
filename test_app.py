import os
import pytest
import database
from app import app

@pytest.fixture
def client(tmp_path):
    # Usar una base de datos SQLite temporal exclusiva para pruebas
    test_db = str(tmp_path / "test_orbita_moche.db")
    database.DB_NAME = test_db
    database.init_db()

    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test_secret_key"

    with app.test_client() as client:
        yield client

def test_01_pagina_inicio_publica(client):
    """Verifica que la portada principal con el reto NASA cargue correctamente."""
    res = client.get("/")
    assert res.status_code == 200
    assert b"MOCHE" in res.data

def test_02_proteccion_ruta_dashboard_sin_login(client):
    """Verifica que un usuario no autenticado sea redirigido al login."""
    res = client.get("/dashboard", follow_redirects=False)
    assert res.status_code == 302
    assert "/login" in res.headers["Location"]

def test_03_registro_e_inicio_sesion_usuario(client):
    """Verifica el registro de un nuevo investigador y su posterior login."""
    res_reg = client.post("/register", data={
        "nombre": "Tester UPRIT",
        "email": "tester@uprit.edu.pe",
        "password": "Password123*",
        "rol": "investigador"
    }, follow_redirects=True)
    assert res_reg.status_code == 200
    assert b"Registro exitoso" in res_reg.data

    res_login = client.post("/login", data={
        "email": "tester@uprit.edu.pe",
        "password": "Password123*"
    }, follow_redirects=True)
    assert res_login.status_code == 200
    assert b"Tester UPRIT" in res_login.data

def test_04_api_datos_satelitales_nasa(client):
    """Verifica que el endpoint de datos satelitales responda con métricas válidas."""
    res = client.get("/api/datos-zona?sector=morrope_san_jose_tinajones")
    assert res.status_code == 200
    data = res.get_json()
    assert data["sector_id"] == "morrope_san_jose_tinajones"
    assert "temperatura_c" in data["metricas"]
    assert "humedad_smap" in data["metricas"]

def test_05_crud_crear_y_listar_reporte(client):
    """Verifica la creación (Create) y visualización (Read) de un reporte en SQLite."""
    client.post("/login", data={
        "email": "investigador@orbitamoche.pe",
        "password": "Investigador2026*"
    })

    res_create = client.post("/reportes/crear", data={
        "sector_id": "morrope_san_jose_tinajones",
        "tipo_pozo": "Pozo Prueba Pytest",
        "salinidad_ppm": "2600.5",
        "observaciones": "Prueba automatizada de alta salinidad"
    }, follow_redirects=True)

    assert res_create.status_code == 200
    assert b"Pozo Prueba Pytest" in res_create.data
    assert b"2600.5" in res_create.data

def test_06_crud_actualizar_y_eliminar_reporte(client):
    """Verifica la actualización (Update) y eliminación (Delete) con rol Admin."""
    client.post("/login", data={
        "email": "admin@orbitamoche.pe",
        "password": "Admin2026*"
    })

    # Actualizar reporte ID 1
    res_edit = client.post("/reportes/editar/1", data={
        "sector_id": "morrope_san_jose_tinajones",
        "tipo_pozo": "Pozo Actualizado Admin",
        "salinidad_ppm": "1500.0",
        "observaciones": "Salinidad moderada tras control"
    }, follow_redirects=True)
    assert res_edit.status_code == 200
    assert b"Pozo Actualizado Admin" in res_edit.data

    # Eliminar reporte ID 1
    res_del = client.post("/reportes/eliminar/1", follow_redirects=True)
    assert res_del.status_code == 200
    assert b"Pozo Actualizado Admin" not in res_del.data

def test_07_cierre_sesion(client):
    """Verifica el cierre de sesión y redirección al inicio."""
    client.post("/login", data={
        "email": "admin@orbitamoche.pe",
        "password": "Admin2026*"
    })
    res_logout = client.get("/logout", follow_redirects=True)
    assert res_logout.status_code == 200
    # Verificamos texto presente en el index.html sin conflictos de tildes
    assert b"NASA" in res_logout.data