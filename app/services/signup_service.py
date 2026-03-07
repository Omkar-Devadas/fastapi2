from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.db.models import SignupSession, VerifiedUser
from app.services.storage_service import save_bytes_to_uploads


@dataclass(frozen=True)
class SignupServiceError(Exception):
    code: str
    message: str


def _generate_otp() -> str:
    return str(random.randint(100000, 999999))


def start_signup(db: Session, email: str, phone: str) -> dict:
    otp = _generate_otp()
    expiry = datetime.utcnow() + timedelta(minutes=5)

    session = SignupSession(
        email=email,
        phone=phone,
        otp1=otp,
        otp1_expiry=expiry,
        status="OTP1_SENT",
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    return {"message": "OTP1 sent", "signup_id": session.signup_id, "otp": otp}


def verify_otp1(db: Session, signup_id: int, otp: str) -> dict:
    session = (
        db.query(SignupSession).filter(SignupSession.signup_id == signup_id).first()
    )

    if not session or session.otp1 != otp:
        raise SignupServiceError(code="INVALID_OTP", message="Invalid OTP")

    if session.otp1_expiry < datetime.utcnow():
        raise SignupServiceError(code="OTP_EXPIRED", message="OTP expired")

    session.status = "OTP1_VERIFIED"
    db.commit()

    return {"message": "OTP1 verified"}


def complete_profile(
    db: Session,
    signup_id: int,
    first_name: str,
    last_name: str,
    *,
    photo_filename: str,
    photo_bytes: bytes,
) -> dict:
    session = (
        db.query(SignupSession)
        .filter(
            SignupSession.signup_id == signup_id,
            SignupSession.status == "OTP1_VERIFIED",
        )
        .first()
    )

    if not session:
        raise SignupServiceError(code="INVALID_SESSION", message="Invalid session")

    photo_path = save_bytes_to_uploads(photo_filename, photo_bytes)

    otp2 = _generate_otp()
    expiry = datetime.utcnow() + timedelta(minutes=5)

    session.first_name = first_name
    session.last_name = last_name
    session.photo_path = photo_path
    session.otp2 = otp2
    session.otp2_expiry = expiry
    session.status = "OTP2_SENT"

    db.commit()

    return {"message": "OTP2 sent", "otp": otp2}


def verify_otp2(db: Session, signup_id: int, otp: str) -> dict:
    session = (
        db.query(SignupSession)
        .filter(
            SignupSession.signup_id == signup_id,
            SignupSession.status == "OTP2_SENT",
        )
        .first()
    )

    if not session or session.otp2 != otp:
        raise SignupServiceError(code="INVALID_OTP", message="Invalid OTP")

    if session.otp2_expiry < datetime.utcnow():
        raise SignupServiceError(code="OTP_EXPIRED", message="OTP expired")

    user = VerifiedUser(
        email=session.email,
        phone=session.phone,
        first_name=session.first_name,
        last_name=session.last_name,
        photo_path=session.photo_path,
    )

    db.add(user)
    session.status = "COMPLETED"
    db.commit()

    return {"message": "Signup completed successfully"}

