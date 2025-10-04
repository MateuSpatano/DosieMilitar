from fastapi import APIRouter
from . import auth, account, manage_file, dashboard, user

router = APIRouter(tags=["Versão 1"])

# Inclui os roteadores de recursos
router.include_router(auth.router, prefix="/authentication")
router.include_router(account.router, prefix="/account")
router.include_router(manage_file.router, prefix="/manage-file")
router.include_router(dashboard.router, prefix="/dashboard")
router.include_router(user.router, prefix="/user")

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "message": "Sistema funcionando"}