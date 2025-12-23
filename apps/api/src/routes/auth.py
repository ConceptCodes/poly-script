from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from poly_db.database import get_db_session
from poly_core.services.auth import AuthService
from poly_core.services.oauth import OAuthService
from poly_core.services.team import TeamService
from poly_core.constants import I18nKeys
from schemas.auth import (
    SignupRequest,
    SignupResponse,
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    LogoutRequest,
    UserResponse,
    ResendVerificationRequest,
    VerifyEmailRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    OAuthAuthURLRequest,
    OAuthCallbackRequest,
)
from dependencies import get_current_user


router = APIRouter(prefix="/v1/auth", tags=["Auth"])


def get_auth_service(db: Session = Depends(get_db_session)) -> AuthService:
    return AuthService(db)


def get_oauth_service(db: Session = Depends(get_db_session)) -> OAuthService:
    return OAuthService(db)


def get_team_service(db: Session = Depends(get_db_session)) -> TeamService:
    return TeamService(db)


@router.post("/signup", response_model=SignupResponse, status_code=status.HTTP_201_CREATED)
def signup(request: SignupRequest, auth_service: AuthService = Depends(get_auth_service)):
    user, team = auth_service.create_user(
        email=request.email,
        password=request.password,
        full_name=request.full_name,
    )

    return SignupResponse(
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
        is_verified=user.is_verified,
    )


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, auth_service: AuthService = Depends(get_auth_service)):
    tokens = auth_service.login(email=request.email, password=request.password)

    return TokenResponse(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        token_type="bearer",
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(request: LogoutRequest, auth_service: AuthService = Depends(get_auth_service)):
    auth_service.logout(refresh_token=request.refresh_token)


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(request: RefreshTokenRequest, auth_service: AuthService = Depends(get_auth_service)):
    tokens = auth_service.refresh_access_token(refresh_token=request.refresh_token)

    return TokenResponse(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        token_type="bearer",
    )


@router.get("/me", response_model=UserResponse)
def get_me(current_user: UserResponse = Depends(get_current_user)):
    return current_user


@router.post("/verify-email", status_code=status.HTTP_204_NO_CONTENT)
def verify_email(request: VerifyEmailRequest, auth_service: AuthService = Depends(get_auth_service)):
    success = auth_service.verify_email(token=request.token)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=I18nKeys.INVALID_VERIFICATION_TOKEN.value,
        )


@router.post("/resend-verification", status_code=status.HTTP_204_NO_CONTENT)
def resend_verification(request: ResendVerificationRequest, auth_service: AuthService = Depends(get_auth_service)):
    auth_service.resend_verification_email(email=request.email)


@router.post("/forgot-password", status_code=status.HTTP_204_NO_CONTENT)
def forgot_password(request: ForgotPasswordRequest, auth_service: AuthService = Depends(get_auth_service)):
    auth_service.send_password_reset_email(email=request.email)


@router.post("/reset-password", status_code=status.HTTP_204_NO_CONTENT)
def reset_password(request: ResetPasswordRequest, auth_service: AuthService = Depends(get_auth_service)):
    success = auth_service.reset_password(token=request.token, new_password=request.new_password)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=I18nKeys.INVALID_RESET_TOKEN.value,
        )


@router.get("/oauth/google", response_model=dict)
def get_oauth_auth_url(request: OAuthAuthURLRequest, oauth_service: OAuthService = Depends(get_oauth_service)):
    auth_url = oauth_service.get_google_auth_url(
        redirect_url=request.redirect_url,
        state=request.state,
    )
    return {"auth_url": auth_url}


@router.post("/oauth/google/callback", response_model=TokenResponse)
def oauth_callback(request: OAuthCallbackRequest, oauth_service: OAuthService = Depends(get_oauth_service)):
    tokens = oauth_service.exchange_google_code(code=request.code, state=request.state)

    return TokenResponse(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        token_type="bearer",
    )
