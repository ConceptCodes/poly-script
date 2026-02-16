import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from poly_core.services.auth_async import AsyncAuthService
from poly_core.services.oauth_async import AsyncOAuthService
from poly_core.services.team_async import AsyncTeamService
from src.config import get_settings
from src.dependencies import get_async_auth_service, get_async_db, get_current_user
from src.schemas.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    LogoutRequest,
    RefreshTokenRequest,
    ResendVerificationRequest,
    ResetPasswordRequest,
    SignupRequest,
    SignupResponse,
    TokenResponse,
    UserResponse,
    VerifyEmailCodeRequest,
    VerifyEmailRequest,
)

router = APIRouter(prefix="/v1/auth", tags=["Auth"])


async def get_oauth_service(
    db: AsyncSession = Depends(get_async_db),
    auth_service: AsyncAuthService = Depends(get_async_auth_service),
) -> AsyncOAuthService:
    """Dependency for OAuth service with async DB session."""
    settings = get_settings()
    return AsyncOAuthService(
        db_session=db,
        google_client_id=settings.GOOGLE_CLIENT_ID or "",
        google_client_secret=settings.GOOGLE_CLIENT_SECRET or "",
        oauth_redirect_url=settings.OAUTH_REDIRECT_URL,
        auth_service=auth_service,
    )


async def get_team_service(
    db: AsyncSession = Depends(get_async_db),
) -> AsyncTeamService:
    """Dependency for Team service with async DB session."""
    return AsyncTeamService(db)


@router.post("/signup", response_model=SignupResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    request: SignupRequest, auth_service: AsyncAuthService = Depends(get_async_auth_service)
):
    try:
        user = await auth_service.create_user(
            email=request.email,
            password=request.password,
            full_name=request.full_name,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    return SignupResponse(
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
        is_verified=user.is_verified,
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest, auth_service: AsyncAuthService = Depends(get_async_auth_service)
):
    try:
        tokens = await auth_service.login(email=request.email, password=request.password)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    return TokenResponse(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        token_type="bearer",
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    request: LogoutRequest, auth_service: AsyncAuthService = Depends(get_async_auth_service)
):
    try:
        await auth_service.logout(refresh_token=request.refresh_token)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    auth_service: AsyncAuthService = Depends(get_async_auth_service),
):
    try:
        tokens = await auth_service.refresh_access_token(refresh_token=request.refresh_token)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    return TokenResponse(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        token_type="bearer",
    )


@router.get("/me", response_model=UserResponse)
def get_me(current_user: UserResponse = Depends(get_current_user)):
    return current_user


@router.post("/verify-email", status_code=status.HTTP_204_NO_CONTENT)
async def verify_email(
    request: VerifyEmailRequest,
    auth_service: AsyncAuthService = Depends(get_async_auth_service),
):
    try:
        await auth_service.verify_email(token=request.token)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.post("/verify-email-code", status_code=status.HTTP_204_NO_CONTENT)
async def verify_email_code(
    request: VerifyEmailCodeRequest,
    auth_service: AsyncAuthService = Depends(get_async_auth_service),
):
    """Verify email using a 6-digit code (simplified version using token as code)."""
    try:
        # For now, treat the code as the verification token
        # In production, you would generate a separate 6-digit code
        await auth_service.verify_email(token=request.code)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.post("/resend-verification", status_code=status.HTTP_204_NO_CONTENT)
async def resend_verification(
    request: ResendVerificationRequest,
    auth_service: AsyncAuthService = Depends(get_async_auth_service),
):
    try:
        await auth_service.resend_verification_email(email=request.email)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.post("/forgot-password", status_code=status.HTTP_204_NO_CONTENT)
async def forgot_password(
    request: ForgotPasswordRequest, auth_service: AsyncAuthService = Depends(get_async_auth_service)
):
    try:
        await auth_service.send_password_reset_email(email=request.email)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.post("/reset-password", status_code=status.HTTP_204_NO_CONTENT)
async def reset_password(
    request: ResetPasswordRequest, auth_service: AsyncAuthService = Depends(get_async_auth_service)
):
    try:
        await auth_service.reset_password(token=request.token, new_password=request.new_password)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.get("/oauth/google", response_model=dict)
async def get_oauth_auth_url(
    redirect_url: str | None = None,
    state: str | None = None,
    code_challenge: str | None = None,
    code_challenge_method: str | None = None,
    oauth_service: AsyncOAuthService = Depends(get_oauth_service),
):
    auth_url = await oauth_service.get_google_auth_url(
        redirect_url=redirect_url,
        state=state,
        code_challenge=code_challenge,
        code_challenge_method=code_challenge_method,
    )
    return {"auth_url": auth_url}


@router.get("/oauth/google/callback", response_model=TokenResponse)
async def oauth_callback(
    code: str,
    state: str | None = None,
    code_verifier: str | None = None,
    oauth_service: AsyncOAuthService = Depends(get_oauth_service),
    auth_service: AsyncAuthService = Depends(get_async_auth_service),
):
    # Handle complete OAuth flow: exchange code → find/create user → generate JWTs
    user_data = await oauth_service.handle_google_oauth_callback(
        code=code, state=state, code_verifier=code_verifier
    )

    # Generate JWTs for the user
    user_id = uuid.UUID(user_data["user_id"])
    access_token = await auth_service.create_access_token(user_id)
    refresh_token = await auth_service.create_refresh_token(user_id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


auth_router = router
