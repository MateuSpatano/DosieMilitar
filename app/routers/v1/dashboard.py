from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from app.dependencies.auth import require_auth, get_user_object
from app.dependencies.dashboard import get_dashboard_data

router = APIRouter()

# Dashboard
@router.get("")
async def get_dashboard_api(
    current_user: dict = Depends(require_auth),
    dashboard_data: dict = Depends(get_dashboard_data)
):
    return JSONResponse({
        "stats": dashboard_data.get("stats"),
        "military_stats": dashboard_data.get("military_stats"),
        "chart_data": dashboard_data.get("chart_data")
    })

# Account
@router.get("/account")
async def get_account_api(user_object = Depends(get_user_object)):
    return JSONResponse({
        "user_data": {
            "id": user_object.id,
            "name": user_object.name,
            "email": user_object.email,
            "role": user_object.role.name,
            "created_at": user_object.created_at.isoformat()
        }
    })