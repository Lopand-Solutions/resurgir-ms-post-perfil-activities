import base64
from hashlib import sha256
import re
from typing import Optional
from fastapi import FastAPI, HTTPException, Body, Request, Depends
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator, ValidationError
from pymongo import MongoClient
from datetime import date, datetime
from bson import ObjectId
import os
import pytz

if os.getenv("TEST_ENV", "true") != "true":
    from mangum import Mangum

app = FastAPI()

# Configuración de MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DATABASE_NAME = "db_resurgir"
COLLECTION_NAME = "cat_perfil_activities_collection"
LOG_EXCEPTION_COLLECTION_NAME = "log_exception_collection"

client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
cat_perfil_activities_collection = db[COLLECTION_NAME]
log_exception_collection = db[LOG_EXCEPTION_COLLECTION_NAME]


response = {
    "code": 0,
    "error": None,
    "message": "",
    "object": None
}

pattern_id = r"[a-fA-F\d]{24}"
pattern_name = r"^[a-zA-ZÁÉÍÓÚáéíóúÑñ0-9\s]+$"
timezone_mexico = pytz.timezone("America/Mexico_City")

# Handler personalizado para errores generales (400)
class CustomHTTPExceptionModel(BaseModel):
    code: int
    error: int
    message: str
    object: dict | None = None

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    # Extraer los detalles de la excepción si están disponibles
    if isinstance(exc.detail, dict):
        detail = exc.detail
    else:
        detail = {
            "code": -1,
            "error": 1000,
            "message": exc.detail if exc.detail else "An error occurred.",
            "object": None,
        }

    # Crear la respuesta personalizada
    response_data = CustomHTTPExceptionModel(**detail)

    return JSONResponse(
        status_code=exc.status_code,
        content=response_data.model_dump()
    )

# Handler personalizado para errores de validación (422)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    try:
        # Personaliza la estructura del error
        custom_errors = [
            {
                "param": error["loc"][1],
                "msg": error["msg"],
                "type": "validation error",
            }
            for error in exc.errors()
        ]

        response.update({
            "code": -1,
            "error": 1000,
            "message": "Validation error.",
            "object": custom_errors
        })

        return JSONResponse(
            status_code=422,
            content=response
        )
    except Exception as e:
        response.update({
            "code": -2,
            "error": 2003,
            "message": "Payload not defined correctly.",
            "object": None
        })
        raise HTTPException(status_code=500, detail=response)

# Pydantic Model
class NameModel(BaseModel):
    Name: str = Field(..., min_length=2, max_length=50, pattern=pattern_name)

    @field_validator("Name")
    def validate_name(cls, v):
        if not re.match(pattern_name, v):
            raise ValueError("Name can only contain letters, numbers, and spaces.")
        return v

@app.get("/")
async def root():
    return {"message": "Microservice is running :)"}

@app.post("/perfilactivities")
async def add_name(data: NameModel):
    try:
        # Crear documento
        new_name_entry = {
            "Name": data.Name,
            "Created_at": datetime.now(),
            "Updated_at": datetime.now(),
            "Active": True
        }

        # Validate unique Name
        if cat_perfil_activities_collection.find_one({"Name": data.Name, "Active": True}):
            response.update({
                "code": -1,
                "error": 1001,
                "message": "The Name is already registered.",
                "object": None
            })
            raise HTTPException(status_code=400, detail=response)

        result = cat_perfil_activities_collection.insert_one(new_name_entry)

        if result.inserted_id:
            response.update({
                "code": 0,
                "message": "Activity Informal Meditation successfully added.",
                "object": {"id": str(result.inserted_id)}
            })
            return response
        else:
            response.update({
                "code": -2,
                "error": 2001,
                "message": "Error adding the Activity Informal Meditation.",
                "object": None
            })
            raise HTTPException(status_code=500, detail=response)

    except HTTPException as e:
        raise e
    except Exception as e:
        # Registrar el error
        log_entry = {
            "IdUser": None,
            "Email": None,
            "Status": "Failed",
            "Error": str(e),
            "Timestamp": datetime.now(timezone_mexico),
            "Microservice": "perfilactivities",
            "Method": "POST"
        }
        log_exception_collection.insert_one(log_entry)

        response.update({
            "code": -2,
            "error": 2002,
            "message": "Error interno en el servidor.",
            "object": None
        })
        raise HTTPException(status_code=500, detail=response)

if os.getenv("TEST_ENV", "true") != "true":
    lambda_handler = Mangum(app, lifespan="off")
