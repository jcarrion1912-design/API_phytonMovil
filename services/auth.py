from __future__ import annotations

from typing import Any

from fastapi import Depends, Header, HTTPException, status
from firebase_admin import auth as firebase_auth

from services.firebase_service import db, normalize_firestore_document


def get_bearer_token(authorization: str | None = Header(default=None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Falta el token de autenticación",
        )
    token = authorization.split(" ", 1)[1].strip()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El token de autenticación está vacío",
        )
    return token


def verify_id_token(token: str) -> dict[str, Any]:
    try:
        decoded = firebase_auth.verify_id_token(token)
        print(
            "[auth] token verificado",
            {
                "uid": decoded.get("uid"),
                "email": decoded.get("email"),
                "aud": decoded.get("aud"),
                "iss": decoded.get("iss"),
            },
        )
        return decoded
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token de Firebase inválido o expirado: {exc}",
        ) from exc


def get_current_admin(
    token: str = Depends(get_bearer_token),
) -> dict[str, Any]:
    decoded_token = verify_id_token(token)
    uid = decoded_token.get("uid")
    email = decoded_token.get("email", "")

    if not uid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudo obtener el UID del usuario autenticado",
        )

    admin_doc = db.collection("admins").document(uid).get()
    if not admin_doc.exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El usuario autenticado no tiene perfil de administrador",
        )

    admin_data = normalize_firestore_document(admin_doc)
    if not admin_data.get("activo", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El perfil de administrador está inactivo",
        )

    admin_data["uid"] = uid
    admin_data["email"] = admin_data.get("email") or email or ""
    admin_data.setdefault("rol", "admin")
    return admin_data


def create_firebase_student_user(
    *,
    uid: str,
    email: str,
    password: str,
    display_name: str = "",
) -> dict[str, Any]:
    try:
        user = firebase_auth.create_user(
            uid=uid,
            email=email,
            password=password,
            display_name=display_name or None,
            email_verified=False,
            disabled=False,
        )
        return user.__dict__
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No se pudo crear el usuario de Firebase Auth: {exc}",
        ) from exc


def update_firebase_student_user(
    *,
    uid: str,
    email: str | None = None,
    password: str | None = None,
    display_name: str | None = None,
    disabled: bool | None = None,
) -> dict[str, Any]:
    try:
        kwargs: dict[str, Any] = {}
        if email is not None:
            kwargs["email"] = email
        if password is not None:
            kwargs["password"] = password
        if display_name is not None:
            kwargs["display_name"] = display_name
        if disabled is not None:
            kwargs["disabled"] = disabled
        user = firebase_auth.update_user(uid, **kwargs)
        return user.__dict__
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No se pudo actualizar el usuario de Firebase Auth: {exc}",
        ) from exc


def delete_firebase_student_user(uid: str) -> None:
    try:
        firebase_auth.delete_user(uid)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No se pudo eliminar el usuario de Firebase Auth: {exc}",
        ) from exc
