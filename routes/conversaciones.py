from fastapi import APIRouter, HTTPException

from models.modelos import Conversacion, ConversacionCreate
from services.firebase_service import db, now_iso, document_payload, query_where

router = APIRouter(prefix="/api/v1/conversaciones", tags=["Conversaciones"])


@router.get("/{idConversacion}", response_model=Conversacion)
def obtener_conversacion(idConversacion: str):
    doc = db.collection("conversaciones").document(idConversacion).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")
    return Conversacion(**document_payload(doc))


@router.get("/estudiante/{idEstudiante}", response_model=list[Conversacion])
def conversaciones_por_estudiante(idEstudiante: str):
    docs = (
        query_where(db.collection("conversaciones"), "idEstudiante", "==", idEstudiante)
        .stream()
    )
    conversaciones = [Conversacion(**document_payload(doc)) for doc in docs]
    return sorted(
        conversaciones,
        key=lambda conversacion: (
            conversacion.fechaActualizacion or conversacion.fechaCreacion or ""
        ),
        reverse=True,
    )


@router.post("/", response_model=Conversacion, status_code=201)
def crear_conversacion(data: ConversacionCreate):
    ref = db.collection("conversaciones").document()
    payload = data.model_dump()
    payload.update(
        {
            "idConversacion": ref.id,
            "fechaCreacion": now_iso(),
            "fechaActualizacion": now_iso(),
        }
    )
    ref.set(payload)
    return Conversacion(**payload)
