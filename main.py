from fastapi import FastAPI
from pydantic import BaseModel
from routes import chatbot

app = FastAPI(title="API ZEUS")
app.include_router(chatbot.router)


class LoginRequest(BaseModel):
    id_estudiante: str
    password: str


class SolicitudAsesorRequest(BaseModel):
    id_estudiante: str
    carrera: str
    telefono: str
    duda: str


class EncuestaRequest(BaseModel):
    id_estudiante: str
    calificacion: int
    comentario: str

@app.get("/")
def home():
    return {"mensaje": "API ZEUS funcionando correctamente"}


@app.get("/saludo")
def saludo():
    return {"mensaje": "Hola desde FastAPI"}


@app.post("/login")
def login(data: LoginRequest):
    return {
        "success": True,
        "id_estudiante": data.id_estudiante,
        "mensaje": "Login correcto"
    }


@app.post("/solicitud-asesor")
def solicitud_asesor(data: SolicitudAsesorRequest):
    return {
        "success": True,
        "mensaje": "Solicitud enviada correctamente",
        "datos": {
            "id_estudiante": data.id_estudiante,
            "carrera": data.carrera,
            "telefono": data.telefono,
            "duda": data.duda
        }
    }


@app.get("/conversaciones/{id_estudiante}")
def obtener_conversaciones(id_estudiante: str):
    return [
        {
            "id": 1,
            "titulo": "Consulta Java",
            "fecha": "2026-06-21"
        },
        {
            "id": 2,
            "titulo": "Consulta MySQL",
            "fecha": "2026-06-20"
        }
    ]


@app.get("/recursos/{id_estudiante}")
def obtener_recursos(id_estudiante: str):
    return [
        {
            "titulo": "Guía Java Básico",
            "tipo": "PDF"
        },
        {
            "titulo": "Manual MySQL",
            "tipo": "PDF"
        }
    ]


@app.get("/perfil/{id_estudiante}")
def obtener_perfil(id_estudiante: str):
    return {
        "id_estudiante": id_estudiante,
        "nombre": "Juan Pérez García",
        "carrera": "Computación e Informática",
        "ciclo": "2",
        "estado": "Activo"
    }


@app.post("/encuesta")
def guardar_encuesta(data: EncuestaRequest):
    return {
        "success": True,
        "mensaje": "Encuesta registrada correctamente",
        "calificacion": data.calificacion,
        "comentario": data.comentario
    }