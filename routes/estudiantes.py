from fastapi import APIRouter, HTTPException

from models.modelos import Estudiante
from services.firebase_service import db, now_iso, normalize_firestore_document

router = APIRouter(prefix="/api/v1/estudiantes", tags=["Estudiantes"])


@router.get("/{idInstitucional}", response_model=Estudiante)
def obtener_estudiante(idInstitucional: str):
    doc = db.collection("estudiantes").document(idInstitucional).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")

    data = normalize_firestore_document(doc)
    data["idInstitucional"] = doc.id
    data["hashContrasena"] = data.get("contrasena", "")

    return Estudiante(**data)


@router.post("/", response_model=Estudiante, status_code=201)
def crear_o_actualizar_estudiante(estudiante: Estudiante):
    if not estudiante.idInstitucional:
        raise HTTPException(status_code=400, detail="idInstitucional es obligatorio")

    payload = estudiante.model_dump(by_alias=True, exclude_none=True)
    payload.setdefault("fechaCreacion", now_iso())
    payload["fechaActualizacion"] = now_iso()

    db.collection("estudiantes").document(estudiante.idInstitucional).set(payload)
    return Estudiante(**payload)


@router.get("/{idInstitucional}/perfil", response_model=Estudiante, include_in_schema=False)
def perfil_compatibilidad(idInstitucional: str):
    return obtener_estudiante(idInstitucional)
