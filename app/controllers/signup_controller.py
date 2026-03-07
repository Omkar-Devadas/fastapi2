from __future__ import annotations

from fastapi import Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.signup_schema import StartSignup, VerifyOTP1, VerifyOTP2
from app.services import signup_service


def start_signup(data: StartSignup, db: Session = Depends(get_db)):
    return signup_service.start_signup(db=db, email=data.email, phone=data.phone)


def verify_otp1(data: VerifyOTP1, db: Session = Depends(get_db)):
    try:
        return signup_service.verify_otp1(db=db, signup_id=data.signup_id, otp=data.otp)
    except signup_service.SignupServiceError as e:
        raise HTTPException(status_code=400, detail=e.message)


def complete_profile(
    signup_id: int,
    first_name: str,
    last_name: str,
    photo: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    try:
        photo_bytes = photo.file.read()
        return signup_service.complete_profile(
            db=db,
            signup_id=signup_id,
            first_name=first_name,
            last_name=last_name,
            photo_filename=photo.filename or "profile.jpg",
            photo_bytes=photo_bytes,
        )
    except signup_service.SignupServiceError as e:
        raise HTTPException(status_code=400, detail=e.message)


def verify_otp2(data: VerifyOTP2, db: Session = Depends(get_db)):
    try:
        return signup_service.verify_otp2(db=db, signup_id=data.signup_id, otp=data.otp)
    except signup_service.SignupServiceError as e:
        raise HTTPException(status_code=400, detail=e.message)

