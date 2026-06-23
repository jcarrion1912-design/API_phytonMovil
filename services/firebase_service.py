from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1 import FieldFilter

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CREDENTIALS = PROJECT_ROOT / "serviceAccountKey.json"


def init_firebase() -> firestore.Client:
    if not firebase_admin._apps:
        credentials_path = Path(
            os.getenv("GOOGLE_APPLICATION_CREDENTIALS", DEFAULT_CREDENTIALS)
        )
        if not credentials_path.exists():
            raise RuntimeError(
                f"No se encontró el archivo de credenciales de Firebase en: {credentials_path}"
            )
        cred = credentials.Certificate(str(credentials_path))
        firebase_admin.initialize_app(cred)
    return firestore.client()


db = init_firebase()


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def serialize_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: serialize_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [serialize_value(item) for item in value]
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


def normalize_firestore_document(document) -> dict[str, Any]:
    payload = document.to_dict() or {}
    normalized = serialize_value(payload)
    normalized["id"] = document.id
    return normalized


def document_payload(document) -> dict[str, Any]:
    return normalize_firestore_document(document)


def query_payload(documents) -> list[dict[str, Any]]:
    return [document_payload(document) for document in documents]


def query_where(collection_ref, field_path: str, op_string: str, value: Any):
    return collection_ref.where(filter=FieldFilter(field_path, op_string, value))
