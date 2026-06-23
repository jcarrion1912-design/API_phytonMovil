from fastapi import APIRouter, HTTPException

from models.modelos import RecursoRecomendado, RecursoRecomendadoCreate
from services.firebase_service import db, now_iso, document_payload, query_where, normalize_firestore_document

router = APIRouter(prefix="/api/v1/recursos", tags=["Recursos"])


def _recurso_response(doc) -> RecursoRecomendado:
    data = normalize_firestore_document(doc)
    data.pop("id", None)
    data["idRecurso"] = doc.id
    return RecursoRecomendado(**data)


@router.get("/", response_model=list[RecursoRecomendado])
def listar_recursos():
    docs = db.collection("recursosRecomendados").stream()
    return [_recurso_response(doc) for doc in docs]


@router.get("/solicitud/{idSolicitud}", response_model=list[RecursoRecomendado])
def recursos_por_solicitud(idSolicitud: str):
    docs = (
        query_where(db.collection("recursosRecomendados"), "idSolicitud", "==", idSolicitud)
        .stream()
    )
    return [_recurso_response(doc) for doc in docs]


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
    payload["idRecurso"] = ref.id
    return RecursoRecomendado(**payload)
