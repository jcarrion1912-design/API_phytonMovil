from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import (
    admin,
    asesores,
    auth,
    chatbot,
    conversaciones,
    encuestas,
    estudiantes,
    mensajes,
    login,
    recursos,
    solicitudes,
)

app = FastAPI(
    title="API ZEUS",
    version="1.0.0",
    description="API backend para la aplicación móvil de asesoría académica ZEUS.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(login.router)
app.include_router(estudiantes.router)
app.include_router(asesores.router)
app.include_router(solicitudes.router)
app.include_router(conversaciones.router)
app.include_router(mensajes.router)
app.include_router(recursos.router)
app.include_router(encuestas.router)
app.include_router(chatbot.router)


@app.get("/", tags=["Sistema"])
def home():
    return {
        "mensaje": "API ZEUS funcionando correctamente",
        "version": "1.0.0",
    }


@app.get("/health", tags=["Sistema"])
def health():
    return {"status": "ok"}
