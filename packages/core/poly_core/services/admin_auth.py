import uuid
from datetime import UTC, datetime, timedelta

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from poly_core.constants import I18nKeys
from poly_db.models import AdminUser
from poly_db.repositories import AdminUserRepository, AuditLogRepository


class AdminAuthService:
    def __init__(
        self,
        db_session: Session,
        jwt_secret: str,
        jwt_expiry_minutes: int,
    ):
        self.db_session = db_session
        self.jwt_secret = jwt_secret
        self.jwt_expiry_minutes = jwt_expiry_minutes

        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash_password(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def verify_password(self, password: str, hashed: str) -> bool:
        return self.pwd_context.verify(password, hashed)

    def create_access_token(self, admin_id: uuid.UUID, role: str) -> str:
        expire = datetime.now(UTC) + timedelta(minutes=self.jwt_expiry_minutes)
        exp_timestamp = int(expire.timestamp())

        payload = {
            "sub": str(admin_id),
            "admin_user_id": str(admin_id),
            "role": role,
            "exp": exp_timestamp,
            "iat": int(datetime.now(UTC).timestamp()),
        }
        return jwt.encode(payload, self.jwt_secret, algorithm="HS256")

    def verify_access_token(self, token: str) -> dict | None:
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=["HS256"])
            return payload
        except JWTError:
            return None

    def _create_audit_log(  # noqa: PLR0913
        self,
        admin_user_id: uuid.UUID | None,
        action: str,
        target_type: str = "admin_auth",
        target_id: str | None = None,
        previous_state: dict | None = None,
        new_state: dict | None = None,
        reason: str | None = None,
    ) -> None:
        """Helper to create audit log entries."""
        try:
            audit_repo = AuditLogRepository(self.db_session)
            audit_repo.create(
                admin_user_id=admin_user_id,
                target_type=target_type,
                target_id=target_id or "",
                action=action,
                previous_state=previous_state,
                new_state=new_state,
                reason=reason,
            )
            self.db_session.commit()
        except Exception:
            # Audit logging should not fail the primary operation
            self.db_session.rollback()

    def login(self, email: str, password: str) -> dict:
        admin_repo = AdminUserRepository(self.db_session)
        admin = admin_repo.get_by_email(email)

        if not admin:
            self._create_audit_log(
                admin_user_id=None,
                action="login_failure",
                target_type="admin_auth",
                target_id=email,
                new_state={"reason": "admin_not_found"},
            )
            raise ValueError(I18nKeys.INVALID_CREDENTIALS.value)

        if not self.verify_password(password, admin.hashed_password):
            self._create_audit_log(
                admin_user_id=admin.id,
                action="login_failure",
                target_type="admin_auth",
                target_id=str(admin.id),
                new_state={"reason": "invalid_password"},
            )
            raise ValueError(I18nKeys.INVALID_CREDENTIALS.value)

        if not admin.is_active:
            self._create_audit_log(
                admin_user_id=admin.id,
                action="login_failure",
                target_type="admin_auth",
                target_id=str(admin.id),
                new_state={"reason": "account_inactive"},
            )
            raise ValueError(I18nKeys.ACCOUNT_INACTIVE.value)

        if admin.is_suspended:
            self._create_audit_log(
                admin_user_id=admin.id,
                action="login_failure",
                target_type="admin_auth",
                target_id=str(admin.id),
                new_state={"reason": "account_suspended"},
            )
            raise ValueError(I18nKeys.ACCOUNT_SUSPENDED.value)

        access_token = self.create_access_token(admin.id, admin.role)
        refresh_token = self._generate_refresh_token()

        # Audit log successful login
        self._create_audit_log(
            admin_user_id=admin.id,
            action="login_success",
            target_type="admin_auth",
            target_id=str(admin.id),
            new_state={
                "email": admin.email,
                "role": admin.role,
                "timestamp": datetime.now(UTC).isoformat(),
            },
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "admin_id": str(admin.id),
            "admin_email": admin.email,
            "admin_full_name": admin.full_name,
            "admin_role": admin.role,
        }

    def create_admin_user(
        self,
        email: str,
        password: str,
        full_name: str,
        role: str,
        created_by_admin_id: uuid.UUID | None = None,
    ) -> AdminUser:
        admin_repo = AdminUserRepository(self.db_session)
        existing = admin_repo.get_by_email(email)
        if existing:
            raise ValueError(I18nKeys.EMAIL_ALREADY_EXISTS.value)

        if role not in ["SUPER_ADMIN", "ADMIN"]:
            raise ValueError("Invalid admin role")

        hashed_password = self.hash_password(password)

        admin = AdminUser(
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            role=role,
            is_active=True,
            is_suspended=False,
        )

        created_admin = admin_repo.create(admin)
        self.db_session.commit()

        # Audit log admin creation
        self._create_audit_log(
            admin_user_id=created_by_admin_id,
            action="create_admin",
            target_type="admin_user",
            target_id=str(created_admin.id),
            new_state={
                "email": email,
                "role": role,
                "full_name": full_name,
                "is_active": True,
                "is_suspended": False,
            },
        )

        return created_admin

    def _generate_refresh_token(self) -> str:
        return uuid.uuid4().hex
