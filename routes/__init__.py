from fastapi import APIRouter
from .hr import router as admin_router
from .candidates import router as candidate_router
from .auth_router import router as auth_router1

router = APIRouter()

router.include_router(auth_router1)
router.include_router(admin_router)
router.include_router(candidate_router)
