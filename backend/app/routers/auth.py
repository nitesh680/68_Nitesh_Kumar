from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.core.deps import get_current_user
from app.core.security import create_access_token, hash_password, verify_password
from app.db.mongo import get_db
from app.schemas.auth import LoginRequest, SignupRequest, TokenResponse, UserPublic

router = APIRouter()


@router.post("/signup", response_model=TokenResponse)
async def signup(payload: SignupRequest, db=Depends(get_db)):
    existing = await db.users.find_one({"email": payload.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    try:
        password_hash = hash_password(payload.password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    user_id = str(uuid4())
    user = {
        "_id": user_id,
        "email": payload.email,
        "name": payload.name,
        "password_hash": password_hash,
        "avatar_url": None,
    }
    await db.users.insert_one(user)

    token = create_access_token(subject=user_id)
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db=Depends(get_db)):
    user = await db.users.find_one({"email": payload.email})
    if not user or not verify_password(payload.password, user.get("password_hash") or ""):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token(subject=user["_id"])
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserPublic)
async def me(user=Depends(get_current_user)):
    return UserPublic(
        id=user["_id"],
        email=user["email"],
        name=user.get("name") or "",
        avatar_url=user.get("avatar_url"),
    )


@router.post("/avatar")
async def upload_avatar(file: UploadFile = File(...), db=Depends(get_db)):
    raise HTTPException(status_code=501, detail="Avatar upload not enabled in this minimal build")
