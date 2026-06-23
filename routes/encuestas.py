from fastapi import APIRouter, HTTPException

from models.modelos import EncuestaCreate, EncuestaSatisfaccion
from services.firebase_service import db, now_iso, document_payload

router = APIRouter(prefix="/api/v1/encuestas", tags=["Encuestas"])


@router.post("/", response_model=EncuestaSatisfaccion, status_code=201)
def crear_encuesta(data: EncuestaCreate):
    ref = db.collection("encuestasSatisfaccion").document()
    payload = data.model_dump()
    payload.update(
        {
            "idEncuesta": ref.id,
            "fechaCreacion": now_iso(),
        }
    )
    ref.set(payload)
    return EncuestaSatisfaccion(**payload)


@router.get("/{idEncuesta}", response_model=EncuestaSatisfaccion)
def obtener_encuesta(idEncuesta: str):
    doc = db.collection("encuestasSatisfaccion").document(idEncuesta).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Encuesta no encontrada")
    return EncuestaSatisfaccion(**document_payload(doc))


@router.get("/estudiante/{idEstudiante}", response_model=list[EncuestaSatisfaccion])
def encuestas_por_estudiante(idEstudiante: str):
    docs = (
        db.collection("encuestasSatisfaccion")
        .where("idEstudiante", "==", idEstudiante)
        .stream()
    )
    return [EncuestaSatisfaccion(**document_payload(doc)) for doc in docs]
