from fastapi import APIRouter

from models.modelos import LoginRequest, LoginResponse
from routes.auth import login as login_versionado

router = APIRouter(tags=["Auth"])


@router.post("/login", response_model=LoginResponse, include_in_schema=False)
def login(credenciales: LoginRequest):
    return login_versionado(credenciales)
