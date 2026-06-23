from fastapi import APIRouter

from models.modelos import ChatResponse, ChatRequest
from services.chatbot_service import responder_chatbot, guardar_mensaje

router = APIRouter(tags=["Chatbot"])

@router.post("/api/v1/chat", response_model=ChatResponse)
@router.post("/api/zeus/chat", response_model=ChatResponse, include_in_schema=False)
def chat_con_zeus(data: ChatRequest):
    guardar_mensaje(data.idConversacion, "estudiante", data.mensaje)
    respuesta = responder_chatbot(data)
    guardar_mensaje(data.idConversacion, "zeus", respuesta)
    return ChatResponse(respuesta=respuesta)
