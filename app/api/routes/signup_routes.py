# app/api/routes/signup_routes.py

import random
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import SignupSession, VerifiedUser
from app.schemas.signup_schema import (
    StartSignup,
    VerifyOTP1,
    CompleteProfile,
    VerifyOTP2
)

router = APIRouter(prefix="/signup", tags=["Signup"])


def generate_otp():
    return str(random.randint(100000, 999999))


# STEP 1 — Start Signup
@router.post("/start")
def start_signup(data: StartSignup, db: Session = Depends(get_db)):

    otp = generate_otp()
    expiry = datetime.utcnow() + timedelta(minutes=5)

    session = SignupSession(
        email=data.email,
        phone=data.phone,
        otp1=otp,
        otp1_expiry=expiry,
        status="OTP1_SENT"
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    return {
        "message": "OTP1 sent",
        "signup_id": session.signup_id,
        "otp": otp  # remove otp in production
    }


# STEP 2 — Verify OTP1
@router.post("/verify-otp1")
def verify_otp1(data: VerifyOTP1, db: Session = Depends(get_db)):

    session = db.query(SignupSession).filter(
        SignupSession.signup_id == data.signup_id
    ).first()

    if not session or session.otp1 != data.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    if session.otp1_expiry < datetime.utcnow():
        raise HTTPException(status_code=400, detail="OTP expired")

    session.status = "OTP1_VERIFIED"
    db.commit()

    return {"message": "OTP1 verified"}


# STEP 3 — Complete Profile + Generate OTP2
@router.post("/complete-profile")
def complete_profile(
    signup_id: int,
    first_name: str,
    last_name: str,
    photo: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    session = db.query(SignupSession).filter(
        SignupSession.signup_id == signup_id,
        SignupSession.status == "OTP1_VERIFIED"
    ).first()

    if not session:
        raise HTTPException(status_code=400, detail="Invalid session")

    photo_path = f"uploads/{photo.filename}"

    with open(photo_path, "wb") as f:
        f.write(photo.file.read())

    otp2 = generate_otp()
    expiry = datetime.utcnow() + timedelta(minutes=5)

    session.first_name = first_name
    session.last_name = last_name
    session.photo_path = photo_path
    session.otp2 = otp2
    session.otp2_expiry = expiry
    session.status = "OTP2_SENT"

    db.commit()

    return {"message": "OTP2 sent", "otp": otp2}  # remove in production


# STEP 4 — Verify OTP2 & Save Final User
@router.post("/verify-otp2")
def verify_otp2(data: VerifyOTP2, db: Session = Depends(get_db)):

    session = db.query(SignupSession).filter(
        SignupSession.signup_id == data.signup_id,
        SignupSession.status == "OTP2_SENT"
    ).first()

    if not session or session.otp2 != data.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    if session.otp2_expiry < datetime.utcnow():
        raise HTTPException(status_code=400, detail="OTP expired")

    user = VerifiedUser(
        email=session.email,
        phone=session.phone,
        first_name=session.first_name,
        last_name=session.last_name,
        photo_path=session.photo_path
    )

    db.add(user)

    session.status = "COMPLETED"
    db.commit()

    return {"message": "Signup completed successfully"}