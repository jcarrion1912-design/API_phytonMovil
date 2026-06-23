from __future__ import annotations

from typing import Optional

from pydantic import AliasChoices, BaseModel, Field


class ChatRequest(BaseModel):
    idConversacion: str
    mensaje: str
    nombre: str = ""
    correo: str = ""
    carrera: str = ""
    ciclo: str = ""
    
class Asesor(BaseModel):
    idAsesor: str = ""
    nombre: str = ""
    telefono: str = ""
    especialidad: str = ""
    disponible: bool = False
    solicitudesActivas: int = 0
    fechaActualizacion: str = ""


class ChatResponse(BaseModel):
    respuesta: str


class Conversacion(BaseModel):
    idConversacion: str = ""
    idSolicitud: str = ""
    idEstudiante: str = ""
    idAsesor: str = ""
    tipo: str = ""
    estado: str = ""
    fechaCreacion: str = ""
    fechaActualizacion: str = ""


class DatosChat(BaseModel):
    mensaje: str
    nombre: str
    correo: str
    carrera: str
    ciclo: str


class EncuestaSatisfaccion(BaseModel):
    idEncuesta: str = ""
    idSolicitud: str = ""
    idEstudiante: str = ""
    calificacion: int = 0
    comentario: str = ""
    fechaCreacion: str = ""


class Estudiante(BaseModel):
    idInstitucional: str = ""
    correoInstitucional: str = ""
    hashContrasena: str = Field(
        default="",
        validation_alias=AliasChoices("contrasena", "hashContrasena"),
        serialization_alias="contrasena",
    )
    nombre: str = ""
    carrera: str = ""
    ciclo: str = ""
    estado: str = ""
    fechaCreacion: str = ""
    fechaActualizacion: str = ""


class Mensaje(BaseModel):
    idMensaje: str = ""
    idConversacion: str = ""
    remitente: str = ""
    contenido: str = ""
    tipoContenido: str = ""
    fechaCreacion: str = ""


class RecursoRecomendado(BaseModel):
    idRecurso: str = ""
    idSolicitud: str = ""
    titulo: str = ""
    tipo: str = ""
    url: str = ""
    carrera: str = ""
    etiquetaDuda: str = ""
    fechaCreacion: str = ""


class SolicitudAsesoria(BaseModel):
    idSolicitud: str = ""
    idEstudiante: str = ""
    idAsesor: str = ""
    carrera: str = ""
    contacto: str = ""
    duda: str = ""
    estado: str = ""
    plazoMinutos: int = 0
    fechaCreacion: str = ""
    fechaAsignacion: str = ""
    fechaCierre: str = ""


class LoginRequest(BaseModel):
    idInstitucional: str
    contrasena: str = Field(
        validation_alias=AliasChoices("contrasena", "password")
    )


class LoginResponse(BaseModel):
    success: bool
    mensaje: str
    estudiante: Optional[Estudiante] = None


class SolicitudAsesoriaCreate(BaseModel):
    idEstudiante: str
    carrera: str
    contacto: str
    duda: str
    idAsesor: str = ""
    plazoMinutos: int = 30


class EncuestaCreate(BaseModel):
    idSolicitud: str
    idEstudiante: str
    calificacion: int = Field(ge=1, le=5)
    comentario: str


class MensajeCreate(BaseModel):
    remitente: str
    contenido: str
    tipoContenido: str = "texto"


class AsesorCreate(BaseModel):
    nombre: str
    telefono: str
    especialidad: str
    disponible: bool = True


class AsesorUpdate(BaseModel):
    nombre: Optional[str] = None
    telefono: Optional[str] = None
    especialidad: Optional[str] = None
    disponible: Optional[bool] = None


class ConversacionCreate(BaseModel):
    idSolicitud: str
    idEstudiante: str
    idAsesor: str
    tipo: str = "asesoria"
    estado: str = "activa"


class AsignarSolicitud(BaseModel):
    idAsesor: str


class CerrarSolicitud(BaseModel):
    idAsesor: Optional[str] = None
    motivo: Optional[str] = None


class RecursoRecomendadoCreate(BaseModel):
    idSolicitud: str
    titulo: str
    tipo: str
    url: str
    carrera: str
    etiquetaDuda: str
