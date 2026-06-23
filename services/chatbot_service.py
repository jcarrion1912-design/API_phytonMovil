from fastapi import HTTPException
from groq import Groq

from config import GROQ_API_KEY
from models.modelos import ChatRequest
from services.firebase_service import db, now_iso, normalize_firestore_document, query_where

client = Groq(api_key=GROQ_API_KEY)

def obtener_historial_conversacion(id_conversacion: str, limite: int = 10):
    docs = (
        query_where(db.collection("mensajes"), "idConversacion", "==", id_conversacion)
        .stream()
    )
    mensajes = []
    for doc in docs:
        data = normalize_firestore_document(doc)
        mensajes.append({
            "remitente": data.get("remitente", ""),
            "contenido": data.get("contenido", ""),
            "fechaCreacion": data.get("fechaCreacion", ""),
        })
    mensajes.sort(key=lambda item: item.get("fechaCreacion", ""))
    return mensajes[-limite:]

def guardar_mensaje(id_conversacion: str, remitente: str, contenido: str, tipo: str = "texto"):
    ref = db.collection("mensajes").document()
    payload = {
        "idMensaje": ref.id,
        "idConversacion": id_conversacion,
        "remitente": remitente,
        "contenido": contenido,
        "tipoContenido": tipo,
        "leido": False,
        "fechaCreacion": now_iso(),
    }
    ref.set(payload)
    return payload

def responder_chatbot(data: ChatRequest) -> str:
    if not GROQ_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="Falta configurar GROQ_API_KEY en el archivo .env",
        )

    historial = obtener_historial_conversacion(data.idConversacion, limite=10)

    prompt = f"""
Eres ZEUS, asistente académico de Cibertec.
Respondes en tono claro, breve, amable y útil.

Datos del estudiante:
- Nombre: {data.nombre}
- Correo: {data.correo}
- Carrera: {data.carrera}
- Ciclo: {data.ciclo}

Reglas:
- Responde solo sobre temas académicos, asesorías, recursos, horarios, notas, trámites o soporte estudiantil.
- Si falta contexto, usa el historial de la conversación.
- No inventes datos.
- Si no sabes algo, recomienda solicitar un asesor.

Historial de conversación:
{chr(10).join([f'{m["remitente"]}: {m["contenido"]}' for m in historial])}
""".strip()

    try:
        chat_completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": data.mensaje},
            ],
        )
        respuesta = chat_completion.choices[0].message.content or ""
        return respuesta
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
