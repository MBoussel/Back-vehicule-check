from pydantic import BaseModel


class UploadResponse(BaseModel):
    file_name: str
    storage_path: str
    file_url: str
    content_type: str