from fastapi import APIRouter, HTTPException

from models.modelos import RecursoRecomendado, RecursoRecomendadoCreate
from services.firebase_service import db, now_iso, document_payload

router = APIRouter(prefix="/api/v1/recursos", tags=["Recursos"])


@router.get("/", response_model=list[RecursoRecomendado])
def listar_recursos():
    docs = db.collection("recursosRecomendados").stream()
    return [RecursoRecomendado(**document_payload(doc)) for doc in docs]


@router.get("/solicitud/{idSolicitud}", response_model=list[RecursoRecomendado])
def recursos_por_solicitud(idSolicitud: str):
    docs = (
        db.collection("recursosRecomendados")
        .where("idSolicitud", "==", idSolicitud)
        .stream()
    )
    return [RecursoRecomendado(**document_payload(doc)) for doc in docs]


@router.post("/", response_model=RecursoRecomendado, status_code=201)
def crear_recurso(data: RecursoRecomendadoCreate):
    ref = db.collection("recursosRecomendados").document()
    payload = data.model_dump()
    payload.update(
        {
            "idRecurso": ref.id,
            "fechaCreacion": now_iso(),
        }
    )
    ref.set(payload)
    return RecursoRecomendado(**payload)
