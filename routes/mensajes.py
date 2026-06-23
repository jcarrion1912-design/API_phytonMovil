from fastapi import APIRouter, HTTPException

from models.modelos import Mensaje, MensajeCreate
from services.firebase_service import db, now_iso, document_payload, query_where

router = APIRouter(prefix="/api/v1/conversaciones", tags=["Mensajes"])


@router.get("/{idConversacion}/mensajes", response_model=list[Mensaje])
def listar_mensajes(idConversacion: str):
    docs = (
        query_where(db.collection("mensajes"), "idConversacion", "==", idConversacion)
        .stream()
    )
    mensajes = [Mensaje(**document_payload(doc)) for doc in docs]
    return sorted(mensajes, key=lambda mensaje: mensaje.fechaCreacion or "")


@router.post("/{idConversacion}/mensajes", response_model=Mensaje, status_code=201)
def crear_mensaje(idConversacion: str, data: MensajeCreate):
    conv_ref = db.collection("conversaciones").document(idConversacion)
    if not conv_ref.get().exists:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")

    ref = db.collection("mensajes").document()
    payload = data.model_dump()
    payload.update(
        {
            "idMensaje": ref.id,
            "idConversacion": idConversacion,
            "fechaCreacion": now_iso(),
        }
    )
    ref.set(payload)
    return Mensaje(**payload)
