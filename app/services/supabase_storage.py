from __future__ import annotations

import mimetypes
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile
from supabase import Client, create_client

from app.core.config import settings


def get_supabase_client() -> Client:
    if not settings.supabase_url or not settings.supabase_key:
        raise HTTPException(
            status_code=500,
            detail="Supabase configuration is missing in .env",
        )

    print("SUPABASE URL:", settings.supabase_url)
    print("SUPABASE KEY:", settings.supabase_key)

    return create_client(settings.supabase_url, settings.supabase_key)


def build_storage_path(filename: str, folder: str = "checks") -> str:
    extension = Path(filename).suffix.lower()
    unique_name = f"{uuid4().hex}{extension}"
    return f"{folder}/{unique_name}"


def _extract_public_url(public_url_response) -> str:
    if isinstance(public_url_response, str):
        return public_url_response

    if isinstance(public_url_response, dict):
        url = public_url_response.get("publicUrl") or public_url_response.get("public_url")
        if isinstance(url, str):
            return url

    raise HTTPException(
        status_code=500,
        detail="Could not generate public URL",
    )


def upload_bytes_to_supabase(
    *,
    file_bytes: bytes,
    filename: str,
    folder: str = "checks",
    content_type: str | None = None,
) -> dict:
    if not filename:
        raise HTTPException(status_code=400, detail="File name is missing")

    if not file_bytes:
        raise HTTPException(status_code=400, detail="File is empty")

    detected_content_type = (
        content_type
        or mimetypes.guess_type(filename)[0]
        or "application/octet-stream"
    )

    storage_path = build_storage_path(filename, folder=folder)
    supabase = get_supabase_client()

    try:
        upload_response = supabase.storage.from_(settings.supabase_storage_bucket).upload(
            path=storage_path,
            file=file_bytes,
            file_options={
                "content-type": detected_content_type,
                "upsert": "false",
            },
        )
        print("UPLOAD RESPONSE:", upload_response)
    except Exception as error:
        print("UPLOAD ERROR:", repr(error))
        raise HTTPException(
            status_code=500,
            detail=f"Upload failed: {repr(error)}",
        ) from error

    try:
        public_url_response = supabase.storage.from_(
            settings.supabase_storage_bucket
        ).get_public_url(storage_path)
        print("PUBLIC URL RESPONSE:", public_url_response)
        file_url = _extract_public_url(public_url_response)
    except Exception as error:
        print("PUBLIC URL ERROR:", repr(error))
        raise HTTPException(
            status_code=500,
            detail=f"Public URL generation failed: {repr(error)}",
        ) from error

    return {
        "file_name": filename,
        "storage_path": storage_path,
        "file_url": file_url,
        "content_type": detected_content_type,
    }


async def upload_file_to_supabase(
    file: UploadFile,
    folder: str = "checks",
) -> dict:
    if not file.filename:
        raise HTTPException(status_code=400, detail="File name is missing")

    file_bytes = await file.read()

    return upload_bytes_to_supabase(
        file_bytes=file_bytes,
        filename=file.filename,
        folder=folder,
        content_type=file.content_type,
    )