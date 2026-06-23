from fastapi import APIRouter, HTTPException

from models.modelos import Asesor, AsesorCreate, AsesorUpdate
from services.firebase_service import db, now_iso, document_payload

router = APIRouter(prefix="/api/v1/asesores", tags=["Asesores"])


@router.get("/", response_model=list[Asesor])
def listar_asesores():
    docs = db.collection("asesores").stream()
    return [Asesor(**document_payload(doc)) for doc in docs]


@router.get("/{idAsesor}", response_model=Asesor)
def obtener_asesor(idAsesor: str):
    doc = db.collection("asesores").document(idAsesor).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Asesor no encontrado")
    return Asesor(**document_payload(doc))


@router.post("/", response_model=Asesor, status_code=201)
def crear_asesor(data: AsesorCreate):
    ref = db.collection("asesores").document()
    payload = data.model_dump()
    payload.update(
        {
            "idAsesor": ref.id,
            "solicitudesActivas": 0,
            "fechaActualizacion": now_iso(),
        }
    )
    ref.set(payload)
    return Asesor(**payload)


@router.patch("/{idAsesor}", response_model=Asesor)
def actualizar_asesor(idAsesor: str, data: AsesorUpdate):
    doc_ref = db.collection("asesores").document(idAsesor)
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Asesor no encontrado")

    payload = {key: value for key, value in data.model_dump().items() if value is not None}
    payload["fechaActualizacion"] = now_iso()
    doc_ref.update(payload)
    actualizado = doc_ref.get()
    return Asesor(**document_payload(actualizado))
