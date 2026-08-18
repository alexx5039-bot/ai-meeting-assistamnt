from fastapi import HTTPException, status
from app.core.security import hash_password, verify_password, create_access_token
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse


class AuthService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def register(self, data: RegisterRequest) -> User:
        existing_user = await self.repository.get_by_email(email=data.email)

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User already exists"
            )
        hashed_password = hash_password(data.password)

        user = await self.repository.create(
            email=data.email,
            hashed_password=hashed_password)

        return user

    async def authenticate(self, email: str, password: str) -> User:
        user = await self.repository.get_by_email(email=email)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        if not verify_password(
            password,
            user.hashed_password
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        return user

    async def login(
            self,
            email: str,
            password: str
    ) -> TokenResponse:

        user = await self.authenticate(email=email, password=password)

        access_token = create_access_token(
            data={"sub": str(user.id)}
        )

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
        )