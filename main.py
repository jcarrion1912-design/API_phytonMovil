from fastapi import FastAPI

app = FastAPI()

@app.get("/saludo")
def saludo():
    return {"mensaje": "Hola desde FastAPI"}