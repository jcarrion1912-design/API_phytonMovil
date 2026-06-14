from fastapi import FastAPI
from routes import chatbot

app = FastAPI(title="API ZEUS")

app.include_router(chatbot.router)

@app.get("/")
def home():
    return {"mensaje": "API ZEUS funcionando correctamente"}

@app.get("/saludo")
def saludo():
    return {"mensaje": "Hola desde FastAPI"}