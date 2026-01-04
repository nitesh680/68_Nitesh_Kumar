import os
import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse

from app.core.deps import get_current_user
from app.core.config import settings
from app.db.mongo import get_db
from app.schemas.users import UserProfileUpdate, UserProfileResponse, AvatarUploadResponse

router = APIRouter(prefix="/api/users", tags=["users"])

AVATAR_DIR = "uploads/avatars"
os.makedirs(AVATAR_DIR, exist_ok=True)


@router.get("/profile", response_model=UserProfileResponse)
async def get_profile(current_user=Depends(get_current_user), db=Depends(get_db)):
    """Get current user profile."""
    users = db["users"]
    user_doc = await users.find_one({"_id": current_user["_id"]})
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserProfileResponse(
        id=str(user_doc["_id"]),
        email=user_doc["email"],
        name=user_doc.get("name", ""),
        mobile=user_doc.get("mobile"),
        date_of_birth=user_doc.get("date_of_birth"),
        avatar_url=user_doc.get("avatar_url"),
        created_at=user_doc.get("created_at")
    )


@router.patch("/profile", response_model=UserProfileResponse)
async def update_profile(
    update_data: UserProfileUpdate,
    current_user=Depends(get_current_user),
    db=Depends(get_db)
):
    """Update current user profile."""
    users = db["users"]
    update_dict = update_data.dict(exclude_unset=True)
    if update_dict.get("date_of_birth"):
        update_dict["date_of_birth"] = update_dict["date_of_birth"].isoformat()
    
    result = await users.update_one(
        {"_id": current_user["_id"]},
        {"$set": update_dict}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    updated_user = await users.find_one({"_id": current_user["_id"]})
    return UserProfileResponse(
        id=str(updated_user["_id"]),
        email=updated_user["email"],
        name=updated_user.get("name", ""),
        mobile=updated_user.get("mobile"),
        date_of_birth=updated_user.get("date_of_birth"),
        avatar_url=updated_user.get("avatar_url"),
        created_at=updated_user.get("created_at")
    )


@router.post("/profile/avatar", response_model=AvatarUploadResponse)
async def upload_avatar(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
    db=Depends(get_db)
):
    """Upload user avatar image."""
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Generate unique filename
    file_ext = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(AVATAR_DIR, unique_filename)
    
    # Save file
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    # Update user avatar_url in database
    avatar_url = f"/{file_path}"
    users = db["users"]
    await users.update_one(
        {"_id": current_user["_id"]},
        {"$set": {"avatar_url": avatar_url}}
    )
    
    return AvatarUploadResponse(avatar_url=avatar_url)
