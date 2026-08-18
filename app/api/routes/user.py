from fastapi import APIRouter, Depends, status

from fastapi.security import OAuth2PasswordRequestForm

from app.core.security import password_hash
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse, UserResponse,
)
from app.services.user import AuthService
from app.db.dependencies import get_user_service


router = APIRouter()

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
        data: RegisterRequest,
        service: AuthService = Depends(get_user_service)
):
    return await service.register(data)

@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
)
async def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        service: AuthService = Depends(get_user_service)
):
    return await service.login(
        email=form_data.username,
        password=form_data.password
    )
