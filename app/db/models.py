# app/models/models.py

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.db.database import Base

class SignupSession(Base):
    __tablename__ = "signup_sessions"

    signup_id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True)
    phone = Column(String, index=True)

    otp1 = Column(String)
    otp1_expiry = Column(DateTime)

    otp2 = Column(String)
    otp2_expiry = Column(DateTime)

    first_name = Column(String)
    last_name = Column(String)
    photo_path = Column(String)

    status = Column(String, default="INITIATED")

    created_at = Column(DateTime(timezone=True), server_default=func.now())


class VerifiedUser(Base):
    __tablename__ = "verified_users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    phone = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    photo_path = Column(String)

    created_at = Column(DateTime(timezone=True), server_default=func.now())