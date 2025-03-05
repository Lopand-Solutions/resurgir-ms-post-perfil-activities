from fastapi.testclient import TestClient
from unittest.mock import patch
import mongomock
import pytest
from bson import ObjectId
from app.main import app, cat_perfil_activities_collection, log_exception_collection

# Crear el cliente de prueba para FastAPI
client = TestClient(app)

# Credenciales de autenticación para las pruebas
auth_credentials = ("admin", "secret")

# Simular una base de datos MongoDB en memoria
mocked_cat_perfil_activities_collection = mongomock.MongoClient().db.cat_perfil_activities_collection
mocked_log_exception_collection = mongomock.MongoClient().db.log_exception_collection

existing_name = "Existing Activity"

# Configuración inicial para las pruebas
def setup_module(module):
    mocked_cat_perfil_activities_collection.insert_one({
        "_id": ObjectId(),
        "Name": existing_name,
        "Created_at": "2024-01-01T00:00:00",
        "Updated_at": "2024-01-01T00:00:00",
        "Active": True
    })

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Microservice is running :)"}

@patch("app.main.cat_perfil_activities_collection", mocked_cat_perfil_activities_collection)
@patch("app.main.log_exception_collection", mocked_log_exception_collection)
def test_add_perfil_activity_success():
    payload = {
        "Name": "New Activity"
    }

    response = client.post("/perfilactivities", json=payload, auth=auth_credentials)

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert data["message"] == "Activity Perfil successfully added."
    assert "id" in data["object"]

    record = mocked_cat_perfil_activities_collection.find_one({
        "Name": payload["Name"],
        "Active": True
    })
    assert record is not None

@patch("app.main.cat_perfil_activities_collection", mocked_cat_perfil_activities_collection)
@patch("app.main.log_exception_collection", mocked_log_exception_collection)
def test_add_perfil_activity_duplicate_name():
    payload = {
        "Name": existing_name
    }

    response = client.post("/perfilactivities", json=payload, auth=auth_credentials)

    assert response.status_code == 400
    data = response.json()
    assert data["code"] == -1
    assert data["message"] == "The Name is already registered."

@patch("app.main.cat_perfil_activities_collection", mocked_cat_perfil_activities_collection)
@patch("app.main.log_exception_collection", mocked_log_exception_collection)
def test_add_perfil_activity_invalid_name():
    payload = {
        "Name": "Título inválido!@#"
    }

    response = client.post("/perfilactivities", json=payload, auth=auth_credentials)

    assert response.status_code == 422
    data = response.json()
    assert data["code"] == -1
    assert data["message"] == "Validation error."
    assert any(error["param"] == "Name" for error in data["object"])
