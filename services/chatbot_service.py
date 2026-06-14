from groq import Groq
from config import GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY)

def responder_chatbot(mensaje: str, estudiante: dict) -> str:
    prompt_sistema = f"""
Eres ZEUS, un asistente virtual académico de Cibertec.

Datos del estudiante:
Nombre: {estudiante.get("nombre")}
Correo: {estudiante.get("correo")}
Carrera: {estudiante.get("carrera")}
Ciclo: {estudiante.get("ciclo")}

Responde solo temas académicos, asesorías, recursos, horarios, notas, trámites o soporte estudiantil.
Si no sabes algo, recomienda solicitar un asesor.
"""

    respuesta = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": prompt_sistema},
            {"role": "user", "content": mensaje}
        ]
    )

    return respuesta.choices[0].message.content