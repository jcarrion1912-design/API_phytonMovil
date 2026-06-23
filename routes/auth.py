from fastapi import APIRouter, HTTPException
from models.modelos import LoginRequest, LoginResponse, Estudiante
from services.firebase_service import db, normalize_firestore_document
# aquí necesitas helper para Firebase Auth / REST API

router = APIRouter(prefix="/api/v1/auth", tags=["Autenticación"])

@router.post("/login", response_model=LoginResponse)
def login(credenciales: LoginRequest):
    doc = db.collection("estudiantes").document(credenciales.idInstitucional).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")

    data = doc.to_dict() or {}
    correo = data.get("correoInstitucional")
    if not correo:
        raise HTTPException(status_code=400, detail="El estudiante no tiene correo institucional")

    # 1. autenticar con Firebase Auth usando correo + contraseña
    # 2. si falla, devolver 401
    # 3. si pasa, devolver perfil SIN contraseña

    estudiante = normalize_firestore_document(doc)
    estudiante["idInstitucional"] = doc.id

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
    return Estudiante(**data)

