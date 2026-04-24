import base64
import io
import uuid

from fastapi import APIRouter, Depends, HTTPException
from PIL import Image as PILImage
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.check import Check
from app.models.user import User
from app.routes.auth import get_current_user
from app.schemas.signature import SignatureUploadRequest, SignatureUploadResponse
from app.services.supabase_storage import upload_bytes_to_supabase

router = APIRouter(prefix="/checks", tags=["Signatures"])


def extract_base64_payload(signature_base64: str, check_id: int, prefix: str) -> tuple[bytes, str, str]:
    if not signature_base64:
        raise HTTPException(status_code=400, detail="Signature is empty")

    mime_type = "image/png"
    encoded_part = signature_base64

    if signature_base64.startswith("data:"):
        try:
            header, encoded_part = signature_base64.split(",", 1)
        except ValueError as error:
            raise HTTPException(status_code=400, detail="Invalid base64 format") from error

        try:
            mime_type = header.split(";")[0].replace("data:", "").strip().lower()
        except Exception:
            mime_type = "image/png"

    allowed_types = {"image/png", "image/jpeg", "image/jpg", "image/webp"}
    if mime_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Unsupported image format")

    try:
        file_bytes = base64.b64decode(encoded_part, validate=True)
    except Exception as error:
        raise HTTPException(status_code=400, detail="Invalid base64 content") from error

    if not file_bytes:
        raise HTTPException(status_code=400, detail="Decoded signature is empty")

    try:
        img = PILImage.open(io.BytesIO(file_bytes))
        img.load()
    except Exception as error:
        raise HTTPException(status_code=400, detail="Decoded file is not a valid image") from error

    output = io.BytesIO()
    img = img.convert("RGBA")
    img.save(output, format="PNG")
    clean_bytes = output.getvalue()

    if not clean_bytes:
        raise HTTPException(status_code=400, detail="Failed to normalize signature image")

    filename = f"{prefix}_signature_check_{check_id}_{uuid.uuid4().hex}.png"
    return clean_bytes, filename, "image/png"


@router.post("/{check_id}/signature", response_model=SignatureUploadResponse)
def upload_check_signature(
    check_id: int,
    payload: SignatureUploadRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _ = current_user

    check = db.get(Check, check_id)
    if check is None:
        raise HTTPException(status_code=404, detail="Check not found")

    file_bytes, filename, mime_type = extract_base64_payload(
        payload.signature_base64,
        check.id,
        "client",
    )

    upload_result = upload_bytes_to_supabase(
        file_bytes=file_bytes,
        filename=filename,
        folder="signatures",
        content_type=mime_type,
    )

    file_url = upload_result.get("file_url")
    if not isinstance(file_url, str) or not file_url.strip():
        raise HTTPException(status_code=500, detail="Upload failed")

    check.signature_url = file_url

    if check.contract is not None:
        check.contract.status = "signed"

    db.commit()
    db.refresh(check)

    return SignatureUploadResponse(
        check_id=check.id,
        signature_url=file_url,
    )


@router.post("/{check_id}/agent-signature", response_model=SignatureUploadResponse)
def upload_agent_signature(
    check_id: int,
    payload: SignatureUploadRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    check = db.get(Check, check_id)
    if check is None:
        raise HTTPException(status_code=404, detail="Check not found")

    if current_user.role.value != "admin" and check.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You cannot sign this check as agent")

    file_bytes, filename, mime_type = extract_base64_payload(
        payload.signature_base64,
        check.id,
        "agent",
    )

    upload_result = upload_bytes_to_supabase(
        file_bytes=file_bytes,
        filename=filename,
        folder="signatures",
        content_type=mime_type,
    )

    file_url = upload_result.get("file_url")
    if not isinstance(file_url, str) or not file_url.strip():
        raise HTTPException(status_code=500, detail="Upload failed")

    check.agent_signature_url = file_url

    db.commit()
    db.refresh(check)

    return SignatureUploadResponse(
        check_id=check.id,
        signature_url=file_url,
    )