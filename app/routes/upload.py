from fastapi import APIRouter, Depends, File, UploadFile

from app.models.user import User
from app.routes.auth import get_current_user
from app.schemas.upload import UploadResponse
from app.services.supabase_storage import upload_file_to_supabase

router = APIRouter(prefix="/uploads", tags=["Uploads"])


@router.post("/check-photo", response_model=UploadResponse)
async def upload_check_photo(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    _ = current_user
    result = await upload_file_to_supabase(file=file, folder="checks")
    return result


@router.post("/license-photo", response_model=UploadResponse)
async def upload_license_photo(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    _ = current_user
    result = await upload_file_to_supabase(file=file, folder="licenses")
    return result


@router.post("/secondary-license-photo", response_model=UploadResponse)
async def upload_secondary_license_photo(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    _ = current_user
    result = await upload_file_to_supabase(file=file, folder="licenses")
    return result