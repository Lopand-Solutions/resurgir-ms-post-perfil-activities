from fastapi.testclient import TestClient
from unittest.mock import patch
import mongomock
import pytest
from bson import ObjectId
from app.main import app, cat_steps_collection, cat_informal_meditation_activities_collection, log_exception_collection

# Crear el cliente de prueba para FastAPI
client = TestClient(app)

# Simular una base de datos MongoDB en memoria
mocked_cat_steps_collection = mongomock.MongoClient().db.cat_steps_collection
mocked_cat_informal_meditation_activities_collection = mongomock.MongoClient().db.cat_informal_meditation_activities_collection
mocked_log_exception_collection = mongomock.MongoClient().db.log_exception_collection

id_step = ObjectId()
existing_title = "Sample Activity"

# Configuración inicial para las pruebas
def setup_module(module):
    mocked_cat_steps_collection.insert_one({"_id": id_step, "Active": True})
    mocked_cat_informal_meditation_activities_collection.insert_one({
        "_id": ObjectId(),
        "Title": existing_title,
        "IdStep": str(id_step),
        "Text": "Sample text",
        "Active": True,
        "Type": "System"
    })

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Microservice is running :)"}

@patch("app.main.cat_steps_collection", mocked_cat_steps_collection)
@patch("app.main.cat_informal_meditation_activities_collection", mocked_cat_informal_meditation_activities_collection)
@patch("app.main.log_exception_collection", mocked_log_exception_collection)
def test_add_activity_success():
    payload = {
        "Title": "New Activity",
        "Indication": "Testing with invalid image.",
        "IdStep": str(id_step),
        "Text": "A new activity description.",
        "Img": "SGVsbG8gd29ybGQ=",
        "Ext": "jpg",
        "Duration": 5
    }

    response = client.post("/activitiesinformalmeditation", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert data["message"] == "Activity Informal Meditation successfully added."
    assert "id" in data["object"]

    record = mocked_cat_informal_meditation_activities_collection.find_one({
        "Title": payload["Title"],
        "IdStep": payload["IdStep"]
    })
    assert record is not None

@patch("app.main.cat_steps_collection", mocked_cat_steps_collection)
@patch("app.main.cat_informal_meditation_activities_collection", mocked_cat_informal_meditation_activities_collection)
@patch("app.main.log_exception_collection", mocked_log_exception_collection)
def test_add_activity_duplicate_title():
    payload = {
        "Title": existing_title,
        "Indication": "Testing with invalid image.",
        "IdStep": str(id_step),
        "Text": "A duplicate title test.",
        "Img": "SGVsbG8gd29ybGQ=",
        "Ext": "png",
        "Duration": 5
    }

    response = client.post("/activitiesinformalmeditation", json=payload)
    
    assert response.status_code == 400
    data = response.json()
    assert data["code"] == -1
    assert data["message"] == "The Title is already registered."

@patch("app.main.cat_steps_collection", mocked_cat_steps_collection)
@patch("app.main.cat_informal_meditation_activities_collection", mocked_cat_informal_meditation_activities_collection)
@patch("app.main.log_exception_collection", mocked_log_exception_collection)
def test_add_activity_invalid_step():
    payload = {
        "Title": "Invalid Step Test",
        "Indication": "Testing with invalid image.",
        "IdStep": str(ObjectId()),  # Nonexistent IdStep
        "Text": "Testing with invalid step ID.",
        "Img": "SGVsbG8gd29ybGQ=",
        "Ext": "jpg",
        "Duration": 5
    }

    response = client.post("/activitiesinformalmeditation", json=payload)

    assert response.status_code == 400
    data = response.json()
    assert data["code"] == -1
    assert data["message"] == "The IdStep does not exist."

@patch("app.main.cat_steps_collection", mocked_cat_steps_collection)
@patch("app.main.cat_informal_meditation_activities_collection", mocked_cat_informal_meditation_activities_collection)
@patch("app.main.log_exception_collection", mocked_log_exception_collection)
def test_add_activity_invalid_img():
    payload = {
        "Title": "Invalid Image Test",
        "Indication": "Testing with invalid image.",
        "IdStep": str(id_step),
        "Text": "Testing with invalid base64 image.",
        "Img": "InvalidBase64String",
        "Ext": "jpg",
        "Duration": 5
    }

    response = client.post("/activitiesinformalmeditation", json=payload)

    assert response.status_code == 422
    data = response.json()
    assert data["code"] == -1
    assert data["message"] == "Validation error."
    assert any(error["param"] == "Img" for error in data["object"])
