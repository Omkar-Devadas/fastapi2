# app/schemas/signup_schema.py

from pydantic import BaseModel, EmailStr

class StartSignup(BaseModel):
    email: EmailStr
    phone: str


class VerifyOTP1(BaseModel):
    signup_id: int
    otp: str


class CompleteProfile(BaseModel):
    signup_id: int
    first_name: str
    last_name: str


class VerifyOTP2(BaseModel):
    signup_id: int
    otp: str