from fastapi import APIRouter
from . import auth, account, manage_file

router = APIRouter(tags=["Versão 1"])

# Inclui os roteadores de recursos
router.include_router(auth.router, prefix="/authentication")
router.include_router(account.router, prefix="/account")
router.include_router(manage_file.router, prefix="/manage-file")