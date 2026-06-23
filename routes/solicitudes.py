from fastapi import APIRouter, HTTPException

from models.modelos import (
    AsignarSolicitud,
    CerrarSolicitud,
    SolicitudAsesoria,
    SolicitudAsesoriaCreate,
)
from services.firebase_service import db, now_iso, document_payload, query_where

router = APIRouter(prefix="/api/v1/solicitudes", tags=["Solicitudes"])


@router.get("/", response_model=list[SolicitudAsesoria])
def listar_solicitudes():
    docs = db.collection("solicitudesAsesoria").stream()
    return [SolicitudAsesoria(**document_payload(doc)) for doc in docs]


@router.get("/{idSolicitud}", response_model=SolicitudAsesoria)
def obtener_solicitud(idSolicitud: str):
    doc = db.collection("solicitudesAsesoria").document(idSolicitud).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    return SolicitudAsesoria(**document_payload(doc))


@router.get("/estudiante/{idEstudiante}", response_model=list[SolicitudAsesoria])
def solicitudes_por_estudiante(idEstudiante: str):
    docs = (
        query_where(db.collection("solicitudesAsesoria"), "idEstudiante", "==", idEstudiante)
        .stream()
    )
    return [SolicitudAsesoria(**document_payload(doc)) for doc in docs]


@router.post("/", response_model=SolicitudAsesoria, status_code=201)
def crear_solicitud(data: SolicitudAsesoriaCreate):
    ref = db.collection("solicitudesAsesoria").document()
    payload = data.model_dump()
    payload.update(
        {
            "idSolicitud": ref.id,
            "estado": "pendiente",
            "fechaCreacion": now_iso(),
            "fechaAsignacion": "",
            "fechaCierre": "",
        }
    )
    ref.set(payload)
    return SolicitudAsesoria(**payload)


@router.patch("/{idSolicitud}/asignar", response_model=SolicitudAsesoria)
def asignar_solicitud(idSolicitud: str, data: AsignarSolicitud):
    doc_ref = db.collection("solicitudesAsesoria").document(idSolicitud)
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")

    payload = {
        "idAsesor": data.idAsesor,
        "estado": "asignada",
        "fechaAsignacion": now_iso(),
    }
    doc_ref.update(payload)
    actualizado = doc_ref.get()
    return SolicitudAsesoria(**document_payload(actualizado))


@router.patch("/{idSolicitud}/cerrar", response_model=SolicitudAsesoria)
def cerrar_solicitud(idSolicitud: str, data: CerrarSolicitud):
    doc_ref = db.collection("solicitudesAsesoria").document(idSolicitud)
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")

    payload = {
        "estado": "cerrada",
        "fechaCierre": now_iso(),
    }
    if data.idAsesor is not None:
        payload["idAsesor"] = data.idAsesor
    doc_ref.update(payload)
    actualizado = doc_ref.get()
    return SolicitudAsesoria(**document_payload(actualizado))
