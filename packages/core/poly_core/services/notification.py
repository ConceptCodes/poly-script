import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from jinja2 import Template

from poly_core.types import EmailTemplateContext


class NotificationService:
    def __init__(  # noqa: PLR0913
        self,
        smtp_host: str,
        smtp_port: int,
        smtp_user: str | None,
        smtp_password: str | None,
        smtp_from: str,
        templates_dir: str,
        app_url: str,
    ):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
        self.smtp_from = smtp_from
        self.templates_dir = Path(templates_dir)
        self.app_url = app_url

    def _send_email(self, to_email: str, subject: str, html_content: str) -> None:
        msg = MIMEMultipart("alternative")
        msg["From"] = self.smtp_from
        msg["To"] = to_email
        msg["Subject"] = subject

        msg.attach(MIMEText(html_content, "html"))

        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            if self.smtp_user and self.smtp_password:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
            server.send_message(msg)

    def _render_template(self, template_name: str, context: EmailTemplateContext) -> str:
        template_path = self.templates_dir / template_name
        with template_path.open(encoding="utf-8") as f:
            template = Template(f.read())
        return template.render(**context)

    def send_verification_email(
        self,
        user_email: str,
        user_name: str,
        token: str,
    ) -> None:
        verification_url = f"{self.app_url}/verify-email?token={token}"
        context: EmailTemplateContext = {
            "user_name": user_name,
            "verification_url": verification_url,
        }
        html_content = self._render_template("verification_email.html", context)
        self._send_email(user_email, "Verify your email address", html_content)

    def send_password_reset_email(
        self,
        user_email: str,
        user_name: str,
        token: str,
    ) -> None:
        reset_url = f"{self.app_url}/reset-password?token={token}"
        context: EmailTemplateContext = {
            "user_name": user_name,
            "reset_url": reset_url,
        }
        html_content = self._render_template("password_reset_email.html", context)
        self._send_email(user_email, "Reset your password", html_content)

    def send_invitation_email(
        self,
        invitee_email: str,
        inviter_name: str,
        team_name: str,
        token: str,
        role: str,
    ) -> None:
        invitation_url = f"{self.app_url}/accept-invitation?token={token}"
        context: EmailTemplateContext = {
            "invitee_name": invitee_email.split("@")[0],
            "inviter_name": inviter_name,
            "team_name": team_name,
            "invitation_url": invitation_url,
            "role": role,
        }
        html_content = self._render_template("team_invitation_email.html", context)
        self._send_email(invitee_email, f"Invitation to join {team_name}", html_content)
