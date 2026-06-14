from fastapi import APIRouter
from models.chatbot_model import ChatRequest, ChatResponse
from services.chatbot_service import responder_chatbot

router = APIRouter(prefix="/chatbot", tags=["Chatbot"])

@router.post("/", response_model=ChatResponse)
def chatbot(request: ChatRequest):
    estudiante_demo = {
        "nombre": "Juan Pérez García",
        "correo": "i20240@cibertec.edu.pe",
        "carrera": "Ingeniería de Sistemas",
        "ciclo": "4° Ciclo"
    }

    respuesta = responder_chatbot(request.mensaje, estudiante_demo)

    return ChatResponse(respuesta=respuesta)