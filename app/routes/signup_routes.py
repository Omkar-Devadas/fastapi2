from fastapi import APIRouter

from app.controllers.signup_controller import (
    complete_profile,
    start_signup,
    verify_otp1,
    verify_otp2,
)

router = APIRouter(prefix="/signup", tags=["Signup"])

router.post("/start")(start_signup)
router.post("/verify-otp1")(verify_otp1)
router.post("/complete-profile")(complete_profile)
router.post("/verify-otp2")(verify_otp2)

