from fastapi import APIRouter, HTTPException

from models.modelos import LoginRequest, LoginResponse, Estudiante
from services.firebase_service import db, normalize_firestore_document

router = APIRouter(prefix="/api/v1/auth", tags=["Autenticación"])


@router.post("/login", response_model=LoginResponse)
def login(credenciales: LoginRequest):
    doc = db.collection("estudiantes").document(credenciales.idInstitucional).get()

    if not doc.exists:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")

    estudiante_raw = doc.to_dict() or {}
    contrasena = estudiante_raw.get("contrasena") or estudiante_raw.get("hashContrasena")

    if contrasena != credenciales.contrasena:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    estudiante = normalize_firestore_document(doc)
    estudiante["idInstitucional"] = doc.id
    estudiante["hashContrasena"] = estudiante.get("contrasena", contrasena)

    return LoginResponse(
        success=True,
        mensaje="Login exitoso",
        estudiante=Estudiante(**estudiante),
    )


@router.get("/me/{idInstitucional}", response_model=Estudiante)
def obtener_perfil(idInstitucional: str):
    doc = db.collection("estudiantes").document(idInstitucional).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")

    data = normalize_firestore_document(doc)
    data["idInstitucional"] = doc.id
    data["hashContrasena"] = data.get("contrasena", "")

    return Estudiante(**data)
