from pydantic import BaseModel


class ChatRequest(BaseModel):
    id_estudiante: str
    mensaje: str


class ChatResponse(BaseModel):
    respuesta: str