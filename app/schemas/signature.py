from pydantic import BaseModel


class SignatureUploadRequest(BaseModel):
    signature_base64: str


class SignatureUploadResponse(BaseModel):
    check_id: int
    signature_url: str