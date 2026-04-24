from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session, joinedload

from app.db.database import get_db
from app.models.check import Check
from app.models.check_photo import CheckPhoto
from app.models.enums import CheckStatus, PhotoType
from app.models.photo_damage import PhotoDamage
from app.models.user import User
from app.routes.auth import get_current_user
from app.schemas.check_photo import CheckPhotoUploadResponse
from app.schemas.photo_damage import (
    PhotoDamageCreate,
    PhotoDamageResponse,
    PhotoDamageUpdate,
)
from app.services.check_photo_rules import is_required_photo_type
from app.services.supabase_storage import upload_file_to_supabase

router = APIRouter(tags=["Check Photos"])


@router.post("/checks/{check_id}/photos", response_model=CheckPhotoUploadResponse)
async def upload_check_photo(
    check_id: int,
    photo_type: Annotated[PhotoType, Form(...)],
    display_order: Annotated[int, Form()] = 0,
    has_damage: Annotated[bool, Form()] = False,
    damage_comment: Annotated[str | None, Form()] = None,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _ = current_user

    check = (
        db.query(Check)
        .options(joinedload(Check.photos))
        .filter(Check.id == check_id)
        .first()
    )
    if check is None:
        raise HTTPException(status_code=404, detail="Check not found")

    existing_photo = (
        db.query(CheckPhoto)
        .filter(
            CheckPhoto.check_id == check_id,
            CheckPhoto.photo_type == photo_type,
        )
        .first()
    )
    if existing_photo is not None:
        raise HTTPException(
            status_code=400,
            detail=(
                f"A photo already exists for step '{photo_type.value}'. "
                "Delete it before uploading a new one."
            ),
        )

    upload_result = await upload_file_to_supabase(file=file, folder="checks")

    db_photo = CheckPhoto(
        check_id=check_id,
        photo_type=photo_type.value,
        file_url=upload_result["file_url"],
        file_name=upload_result["file_name"],
        display_order=display_order,
        has_damage=has_damage,
        damage_comment=damage_comment,
    )

    db.add(db_photo)
    db.commit()
    db.refresh(db_photo)

    return db_photo


@router.delete("/check-photos/{photo_id}")
def delete_check_photo(
    photo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _ = current_user

    photo = (
        db.query(CheckPhoto)
        .options(
            joinedload(CheckPhoto.check).joinedload(Check.photos),
            joinedload(CheckPhoto.damages),
        )
        .filter(CheckPhoto.id == photo_id)
        .first()
    )

    if photo is None:
        raise HTTPException(status_code=404, detail="Photo not found")

    check = photo.check
    if check is None:
        raise HTTPException(status_code=404, detail="Parent check not found")

    photo_type = photo.photo_type

    db.delete(photo)
    db.flush()

    remaining_same_type = (
        db.query(CheckPhoto)
        .filter(
            CheckPhoto.check_id == check.id,
            CheckPhoto.photo_type == photo_type,
        )
        .first()
    )

    if (
        check.status == CheckStatus.COMPLETED
        and is_required_photo_type(photo_type)
        and remaining_same_type is None
    ):
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=(
                f"Cannot delete required photo '{photo_type.value}' "
                "from a completed check"
            ),
        )

    db.commit()

    return {"message": "Photo deleted"}


@router.post("/check-photos/{photo_id}/damages", response_model=PhotoDamageResponse)
def create_photo_damage(
    photo_id: int,
    payload: PhotoDamageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _ = current_user

    photo = (
        db.query(CheckPhoto)
        .options(joinedload(CheckPhoto.damages))
        .filter(CheckPhoto.id == photo_id)
        .first()
    )

    if photo is None:
        raise HTTPException(status_code=404, detail="Photo not found")

    db_damage = PhotoDamage(
        check_photo_id=photo_id,
        x_percent=payload.x_percent,
        y_percent=payload.y_percent,
        comment=payload.comment,
        severity=payload.severity,
        damage_type=payload.damage_type,
    )

    db.add(db_damage)

    photo.has_damage = True
    if payload.comment and not photo.damage_comment:
        photo.damage_comment = payload.comment

    db.commit()
    db.refresh(db_damage)

    return db_damage


@router.put("/photo-damages/{damage_id}", response_model=PhotoDamageResponse)
def update_photo_damage(
    damage_id: int,
    payload: PhotoDamageUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _ = current_user

    damage = (
        db.query(PhotoDamage)
        .options(joinedload(PhotoDamage.photo))
        .filter(PhotoDamage.id == damage_id)
        .first()
    )

    if damage is None:
        raise HTTPException(status_code=404, detail="Damage not found")

    update_data = payload.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(damage, key, value)

    if damage.photo is not None:
        damage.photo.has_damage = True
        if payload.comment is not None and payload.comment.strip():
            damage.photo.damage_comment = payload.comment

    db.commit()
    db.refresh(damage)

    return damage


@router.delete("/photo-damages/{damage_id}")
def delete_photo_damage(
    damage_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _ = current_user

    damage = (
        db.query(PhotoDamage)
        .options(joinedload(PhotoDamage.photo).joinedload(CheckPhoto.damages))
        .filter(PhotoDamage.id == damage_id)
        .first()
    )

    if damage is None:
        raise HTTPException(status_code=404, detail="Damage not found")

    photo = damage.photo
    if photo is None:
        raise HTTPException(status_code=404, detail="Parent photo not found")

    db.delete(damage)
    db.flush()

    remaining_damages_count = (
        db.query(PhotoDamage)
        .filter(PhotoDamage.check_photo_id == photo.id)
        .count()
    )

    if remaining_damages_count == 0:
        photo.has_damage = False
        photo.damage_comment = None

    db.commit()

    return {"message": "Damage deleted"}