from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from firebase_admin import auth as firebase_auth

from models.modelos import (
    Admin,
    AdminSummary,
    Asesor,
    AsesorCreate,
    AsesorUpdate,
    EstudianteAdmin,
    EstudianteAdminCreate,
    EstudianteAdminUpdate,
    RecursoRecomendado,
    RecursoRecomendadoCreate,
    RecursoRecomendadoUpdate,
    SolicitudAsesoria,
)
from services.auth import (
    create_firebase_student_user,
    delete_firebase_student_user,
    get_current_admin,
    update_firebase_student_user,
)
from services.firebase_service import db, now_iso, normalize_firestore_document, query_where

router = APIRouter(prefix="/api/v1/admin", tags=["Administración"])


def _student_response(doc) -> EstudianteAdmin:
    data = normalize_firestore_document(doc)
    data.pop("id", None)
    data.pop("contrasena", None)
    data.pop("hashContrasena", None)
    data["idInstitucional"] = doc.id
    return EstudianteAdmin(**data)


def _asesor_response(doc) -> Asesor:
    data = normalize_firestore_document(doc)
    data.pop("id", None)
    data["idAsesor"] = doc.id
    return Asesor(**data)


def _doc_list(collection_name: str, model):
    docs = db.collection(collection_name).stream()
    return [model(**normalize_firestore_document(doc)) for doc in docs]


@router.get("/perfil", response_model=Admin)
def obtener_perfil_admin(admin: dict = Depends(get_current_admin)):
    return Admin(**admin)


@router.get("/me", response_model=Admin)
def obtener_me_admin(admin: dict = Depends(get_current_admin)):
    return Admin(**admin)


@router.get("/resumen", response_model=AdminSummary)
def obtener_resumen_admin(admin: dict = Depends(get_current_admin)):
    estudiantes_ref = db.collection("estudiantes")
    asesores_ref = db.collection("asesores")
    solicitudes_ref = db.collection("solicitudes")
    conversaciones_ref = db.collection("conversaciones")
    mensajes_ref = db.collection("mensajes")
    encuestas_ref = db.collection("encuestasSatisfaccion")
    recursos_ref = db.collection("recursosRecomendados")

    estudiantes_docs = estudiantes_ref.get()
    asesores_docs = asesores_ref.get()
    solicitudes_docs = solicitudes_ref.get()
    conversaciones_docs = conversaciones_ref.get()
    mensajes_docs = mensajes_ref.get()
    encuestas_docs = encuestas_ref.get()
    recursos_docs = recursos_ref.get()

    estudiantes_activos = len(query_where(estudiantes_ref, "estado", "==", "activo").get())
    asesores_disponibles = len(query_where(asesores_ref, "disponible", "==", True).get())
    solicitudes_pendientes = len(query_where(solicitudes_ref, "estado", "==", "pendiente").get())
    solicitudes_en_atencion = len(query_where(solicitudes_ref, "estado", "==", "en_atencion").get())
    solicitudes_resueltas = len(query_where(solicitudes_ref, "estado", "==", "resuelto").get())
    conversaciones_activas = len(query_where(conversaciones_ref, "estado", "==", "activa").get())

    return AdminSummary(
        totalEstudiantes=len(estudiantes_docs),
        estudiantesActivos=estudiantes_activos,
        totalAsesores=len(asesores_docs),
        asesoresDisponibles=asesores_disponibles,
        solicitudesPendientes=solicitudes_pendientes,
        solicitudesEnAtencion=solicitudes_en_atencion,
        solicitudesResueltas=solicitudes_resueltas,
        conversacionesActivas=conversaciones_activas,
        mensajesTotales=len(mensajes_docs),
        encuestasTotales=len(encuestas_docs),
        recursosRecomendados=len(recursos_docs),
    )


@router.get("/estudiantes", response_model=list[EstudianteAdmin])
def listar_estudiantes(admin: dict = Depends(get_current_admin)):
    docs = db.collection("estudiantes").order_by("fechaCreacion", direction="DESCENDING").stream()
    return [_student_response(doc) for doc in docs]


@router.get("/estudiantes/{idInstitucional}", response_model=EstudianteAdmin)
def obtener_estudiante_admin(idInstitucional: str, admin: dict = Depends(get_current_admin)):
    doc = db.collection("estudiantes").document(idInstitucional).get()
    if not doc.exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estudiante no encontrado")
    return _student_response(doc)


@router.post("/estudiantes", response_model=EstudianteAdmin, status_code=status.HTTP_201_CREATED)
def crear_estudiante_admin(data: EstudianteAdminCreate, admin: dict = Depends(get_current_admin)):
    doc_ref = db.collection("estudiantes").document(data.idInstitucional)
    if doc_ref.get().exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El estudiante ya existe")

    try:
        firebase_auth.get_user(data.idInstitucional)
        create_auth_user = False
    except firebase_auth.UserNotFoundError:
        create_auth_user = True

    if create_auth_user:
        create_firebase_student_user(
            uid=data.idInstitucional,
            email=data.correoInstitucional,
            password=data.contrasena,
            display_name=data.nombre,
        )
    else:
        update_firebase_student_user(
            uid=data.idInstitucional,
            email=data.correoInstitucional,
            password=data.contrasena,
            display_name=data.nombre,
        )

    payload = {
        "correoInstitucional": data.correoInstitucional,
        "email": data.email or data.correoInstitucional,
        "nombre": data.nombre,
        "carrera": data.carrera,
        "ciclo": data.ciclo,
        "estado": data.estado,
        "fotoUrl": data.fotoUrl,
        "telefono": data.telefono,
        "fechaCreacion": now_iso(),
        "fechaActualizacion": now_iso(),
    }

    try:
        doc_ref.set(payload)
    except Exception as exc:
        delete_firebase_student_user(data.idInstitucional)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"No se pudo guardar el estudiante en Firestore: {exc}",
        ) from exc

    return _student_response(doc_ref.get())


@router.patch("/estudiantes/{idInstitucional}", response_model=EstudianteAdmin)
def actualizar_estudiante_admin(
    idInstitucional: str,
    data: EstudianteAdminUpdate,
    admin: dict = Depends(get_current_admin),
):
    doc_ref = db.collection("estudiantes").document(idInstitucional)
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estudiante no encontrado")

    payload = {key: value for key, value in data.model_dump().items() if value is not None}
    if "contrasena" in payload or "correoInstitucional" in payload or "nombre" in payload:
        update_firebase_student_user(
            uid=idInstitucional,
            email=payload.get("correoInstitucional"),
            password=payload.get("contrasena"),
            display_name=payload.get("nombre"),
        )

    payload.pop("contrasena", None)
    if "correoInstitucional" in payload and "email" not in payload:
        payload["email"] = payload["correoInstitucional"]
    payload["fechaActualizacion"] = now_iso()
    doc_ref.update(payload)
    return _student_response(doc_ref.get())


@router.delete("/estudiantes/{idInstitucional}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_estudiante_admin(idInstitucional: str, admin: dict = Depends(get_current_admin)):
    doc_ref = db.collection("estudiantes").document(idInstitucional)
    if not doc_ref.get().exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estudiante no encontrado")

    doc_ref.delete()
    delete_firebase_student_user(idInstitucional)
    return None


@router.get("/asesores", response_model=list[Asesor])
def listar_asesores(admin: dict = Depends(get_current_admin)):
    docs = db.collection("asesores").order_by("fechaCreacion", direction="DESCENDING").stream()
    return [_asesor_response(doc) for doc in docs]


@router.get("/asesores/{idAsesor}", response_model=Asesor)
def obtener_asesor_admin(idAsesor: str, admin: dict = Depends(get_current_admin)):
    doc = db.collection("asesores").document(idAsesor).get()
    if not doc.exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asesor no encontrado")
    return _asesor_response(doc)


@router.post("/asesores", response_model=Asesor, status_code=status.HTTP_201_CREATED)
def crear_asesor_admin(data: AsesorCreate, admin: dict = Depends(get_current_admin)):
    ref = db.collection("asesores").document(data.idAsesor)
    if ref.get().exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El asesor ya existe")

    payload = data.model_dump()
    payload.update(
        {
            "solicitudesActivas": 0,
            "fechaCreacion": now_iso(),
            "fechaActualizacion": now_iso(),
        }
    )
    ref.set(payload)
    payload["idAsesor"] = ref.id
    return Asesor(**payload)


@router.patch("/asesores/{idAsesor}", response_model=Asesor)
def actualizar_asesor_admin(idAsesor: str, data: AsesorUpdate, admin: dict = Depends(get_current_admin)):
    doc_ref = db.collection("asesores").document(idAsesor)
    if not doc_ref.get().exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asesor no encontrado")

    payload = {key: value for key, value in data.model_dump().items() if value is not None}
    payload["fechaActualizacion"] = now_iso()
    doc_ref.update(payload)
    return _asesor_response(doc_ref.get())


@router.delete("/asesores/{idAsesor}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_asesor_admin(idAsesor: str, admin: dict = Depends(get_current_admin)):
    doc_ref = db.collection("asesores").document(idAsesor)
    if not doc_ref.get().exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asesor no encontrado")
    doc_ref.delete()
    return None


@router.get("/recursos", response_model=list[RecursoRecomendado])
def listar_recursos_admin(admin: dict = Depends(get_current_admin)):
    docs = db.collection("recursosRecomendados").order_by("fechaCreacion", direction="DESCENDING").stream()
    recursos: list[RecursoRecomendado] = []
    for doc in docs:
        data = normalize_firestore_document(doc)
        data.pop("id", None)
        data["idRecurso"] = doc.id
        recursos.append(RecursoRecomendado(**data))
    return recursos


@router.get("/recursos/{idRecurso}", response_model=RecursoRecomendado)
def obtener_recurso_admin(idRecurso: str, admin: dict = Depends(get_current_admin)):
    doc = db.collection("recursosRecomendados").document(idRecurso).get()
    if not doc.exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recurso no encontrado")
    data = normalize_firestore_document(doc)
    data.pop("id", None)
    data["idRecurso"] = doc.id
    return RecursoRecomendado(**data)


@router.post("/recursos", response_model=RecursoRecomendado, status_code=status.HTTP_201_CREATED)
def crear_recurso_admin(data: RecursoRecomendadoCreate, admin: dict = Depends(get_current_admin)):
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


@router.patch("/recursos/{idRecurso}", response_model=RecursoRecomendado)
def actualizar_recurso_admin(
    idRecurso: str,
    data: RecursoRecomendadoUpdate,
    admin: dict = Depends(get_current_admin),
):
    doc_ref = db.collection("recursosRecomendados").document(idRecurso)
    if not doc_ref.get().exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recurso no encontrado")

    payload = {key: value for key, value in data.model_dump().items() if value is not None}
    if payload:
        payload["fechaActualizacion"] = now_iso()
        doc_ref.update(payload)
    data_doc = normalize_firestore_document(doc_ref.get())
    data_doc.pop("id", None)
    data_doc["idRecurso"] = doc_ref.id
    return RecursoRecomendado(**data_doc)


@router.delete("/recursos/{idRecurso}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_recurso_admin(idRecurso: str, admin: dict = Depends(get_current_admin)):
    doc_ref = db.collection("recursosRecomendados").document(idRecurso)
    if not doc_ref.get().exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recurso no encontrado")
    doc_ref.delete()
    return None


@router.get("/solicitudes-recientes", response_model=list[SolicitudAsesoria])
def solicitudes_recientes(cantidad: int = 8, admin: dict = Depends(get_current_admin)):
    docs = (
        db.collection("solicitudes")
        .order_by("fechaCreacion", direction="DESCENDING")
        .limit(cantidad)
        .get()
    )
    solicitudes: list[SolicitudAsesoria] = []
    for doc in docs:
        data = normalize_firestore_document(doc)
        data["idSolicitud"] = doc.id
        solicitudes.append(SolicitudAsesoria(**data))
    return solicitudes


@router.get("/asesores-recientes", response_model=list[Asesor])
def asesores_recientes(cantidad: int = 6, admin: dict = Depends(get_current_admin)):
    docs = (
        db.collection("asesores")
        .order_by("fechaCreacion", direction="DESCENDING")
        .limit(cantidad)
        .get()
    )
    asesores: list[Asesor] = []
    for doc in docs:
        asesores.append(_asesor_response(doc))
    return asesores


@router.get("/estudiantes-recientes", response_model=list[EstudianteAdmin])
def estudiantes_recientes(cantidad: int = 6, admin: dict = Depends(get_current_admin)):
    docs = (
        db.collection("estudiantes")
        .order_by("fechaCreacion", direction="DESCENDING")
        .limit(cantidad)
        .get()
    )
    estudiantes: list[EstudianteAdmin] = []
    for doc in docs:
        estudiantes.append(_student_response(doc))
    return estudiantes
