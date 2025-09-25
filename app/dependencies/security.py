from fastapi import Request, Form, HTTPException, status
from app.security import verify_csrf_token

def validate_csrf_token(
    request: Request,
    csrf_token: str = Form(...)
) -> bool:
    """Valida o token CSRF"""
    session_token = request.session.get("csrf_token")
    if not verify_csrf_token(csrf_token, session_token):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token CSRF inválido"
        )
    return True