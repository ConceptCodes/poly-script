from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260201_191007"
down_revision: Union[str, Sequence[str], None] = "b1c2d3e4f5g6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add comprehensive indexes for performance optimization."""
    
    # Users table indexes
    # - already has: email (unique)
    op.create_index('ix_users_is_verified', 'users', ['is_verified'])
    op.create_index('ix_users_is_active', 'users', ['is_active'])
    op.create_index('ix_users_is_suspended', 'users', ['is_suspended'])
    op.create_index('ix_users_deleted_at', 'users', ['deleted_at'])
    op.create_index('ix_users_verification_token', 'users', ['verification_token'])
    
    # Teams table indexes
    op.create_index('ix_teams_plan', 'teams', ['plan'])
    op.create_index('ix_teams_is_suspended', 'teams', ['is_suspended'])
    op.create_index('ix_teams_stripe_customer_id', 'teams', ['stripe_customer_id'])
    op.create_index('ix_teams_stripe_subscription_id', 'teams', ['stripe_subscription_id'])
    op.create_index('ix_teams_deleted_at', 'teams', ['deleted_at'])
    op.create_index('ix_teams_created_at', 'teams', ['created_at'])
    
    # Team members table indexes
    # - already has: uq_team_user (team_id, user_id)
    op.create_index('ix_team_members_team_id', 'team_members', ['team_id'])
    op.create_index('ix_team_members_user_id', 'team_members', ['user_id'])
    op.create_index('ix_team_members_role', 'team_members', ['role'])
    
    # Transcription jobs table indexes
    op.create_index('ix_transcription_jobs_team_id', 'transcription_jobs', ['team_id'])
    op.create_index('ix_transcription_jobs_status', 'transcription_jobs', ['status'])
    op.create_index('ix_transcription_jobs_team_status', 'transcription_jobs', ['team_id', 'status'])
    op.create_index('ix_transcription_jobs_started_at', 'transcription_jobs', ['started_at'])
    op.create_index('ix_transcription_jobs_finished_at', 'transcription_jobs', ['finished_at'])
    op.create_index('ix_transcription_jobs_created_at', 'transcription_jobs', ['created_at'])
    op.create_index('ix_transcription_jobs_deleted_at', 'transcription_jobs', ['deleted_at'])
    
    # Audio assets table indexes
    op.create_index('ix_audio_assets_job_id', 'audio_assets', ['job_id'])
    op.create_index('ix_audio_assets_created_at', 'audio_assets', ['created_at'])
    op.create_index('ix_audio_assets_deleted_at', 'audio_assets', ['deleted_at'])
    
    # Transcripts table indexes
    op.create_index('ix_transcripts_job_id', 'transcripts', ['job_id'])
    op.create_index('ix_transcripts_language', 'transcripts', ['language'])
    op.create_index('ix_transcripts_created_at', 'transcripts', ['created_at'])
    op.create_index('ix_transcripts_deleted_at', 'transcripts', ['deleted_at'])
    
    # Transcript edits table indexes
    op.create_index('ix_transcript_edits_transcript_id', 'transcript_edits', ['transcript_id'])
    op.create_index('ix_transcript_edits_user_id', 'transcript_edits', ['user_id'])
    op.create_index('ix_transcript_edits_created_at', 'transcript_edits', ['created_at'])
    
    # Translation artifacts table indexes
    op.create_index('ix_translation_artifacts_job_id', 'translation_artifacts', ['job_id'])
    op.create_index('ix_translation_artifacts_status', 'translation_artifacts', ['status'])
    op.create_index('ix_translation_artifacts_target_language', 'translation_artifacts', ['target_language'])
    op.create_index('ix_translation_artifacts_created_at', 'translation_artifacts', ['created_at'])
    
    # Team invitations table indexes
    # - already has: email, token (both indexed)
    op.create_index('ix_team_invitations_team_id', 'team_invitations', ['team_id'])
    op.create_index('ix_team_invitations_expires_at', 'team_invitations', ['expires_at'])
    op.create_index('ix_team_invitations_accepted_at', 'team_invitations', ['accepted_at'])
    
    # Refresh tokens table indexes
    # - already has: token (unique, indexed)
    op.create_index('ix_refresh_tokens_user_id', 'refresh_tokens', ['user_id'])
    op.create_index('ix_refresh_tokens_expires_at', 'refresh_tokens', ['expires_at'])
    op.create_index('ix_refresh_tokens_revoked', 'refresh_tokens', ['revoked'])
    op.create_index('ix_refresh_tokens_created_at', 'refresh_tokens', ['created_at'])
    
    # OAuth accounts table indexes
    # - already has: uq_provider_user (provider, provider_user_id)
    op.create_index('ix_oauth_accounts_user_id', 'oauth_accounts', ['user_id'])
    op.create_index('ix_oauth_accounts_provider', 'oauth_accounts', ['provider'])
    
    # Password resets table indexes
    # - already has: token (unique, indexed)
    op.create_index('ix_password_resets_user_id', 'password_resets', ['user_id'])
    op.create_index('ix_password_resets_expires_at', 'password_resets', ['expires_at'])
    op.create_index('ix_password_resets_used_at', 'password_resets', ['used_at'])
    
    # Admin users table indexes
    # - already has: email (unique, indexed)
    op.create_index('ix_admin_users_is_active', 'admin_users', ['is_active'])
    op.create_index('ix_admin_users_is_suspended', 'admin_users', ['is_suspended'])
    op.create_index('ix_admin_users_role', 'admin_users', ['role'])
    op.create_index('ix_admin_users_deleted_at', 'admin_users', ['deleted_at'])
    
    # Subscriptions table indexes
    # - already has: stripe_subscription_id (unique, indexed)
    op.create_index('ix_subscriptions_team_id', 'subscriptions', ['team_id'])
    op.create_index('ix_subscriptions_status', 'subscriptions', ['status'])
    op.create_index('ix_subscriptions_plan_id', 'subscriptions', ['plan_id'])
    op.create_index('ix_subscriptions_current_period_start', 'subscriptions', ['current_period_start'])
    op.create_index('ix_subscriptions_current_period_end', 'subscriptions', ['current_period_end'])
    
    # Credit purchases table indexes
    # - already has: stripe_session_id (unique, indexed)
    op.create_index('ix_credit_purchases_team_id', 'credit_purchases', ['team_id'])
    op.create_index('ix_credit_purchases_created_at', 'credit_purchases', ['created_at'])
    
    # Invoices table indexes
    # - already has: stripe_invoice_id (unique, indexed)
    op.create_index('ix_invoices_team_id', 'invoices', ['team_id'])
    op.create_index('ix_invoices_status', 'invoices', ['status'])
    op.create_index('ix_invoices_period_start', 'invoices', ['period_start'])
    op.create_index('ix_invoices_period_end', 'invoices', ['period_end'])
    op.create_index('ix_invoices_created_at', 'invoices', ['created_at'])
    
    # Usage logs table indexes
    op.create_index('ix_usage_logs_team_id', 'usage_logs', ['team_id'])
    op.create_index('ix_usage_logs_job_id', 'usage_logs', ['job_id'])
    op.create_index('ix_usage_logs_action', 'usage_logs', ['action'])
    op.create_index('ix_usage_logs_created_at', 'usage_logs', ['created_at'])
    op.create_index('ix_usage_logs_team_action_created', 'usage_logs', ['team_id', 'action', 'created_at'])
    
    # User settings table indexes
    op.create_index('ix_user_settings_user_id', 'user_settings', ['user_id'])
    
    # Audit logs table indexes
    op.create_index('ix_audit_logs_admin_user_id', 'audit_logs', ['admin_user_id'])
    op.create_index('ix_audit_logs_target_type', 'audit_logs', ['target_type'])
    op.create_index('ix_audit_logs_action', 'audit_logs', ['action'])
    op.create_index('ix_audit_logs_created_at', 'audit_logs', ['created_at'])
    op.create_index('ix_audit_logs_target', 'audit_logs', ['target_type', 'target_id'])
    
    # Payment methods table indexes
    # - already has: stripe_payment_method_id (unique, indexed)
    op.create_index('ix_payment_methods_team_id', 'payment_methods', ['team_id'])
    op.create_index('ix_payment_methods_is_default', 'payment_methods', ['is_default'])


def downgrade() -> None:
    """Remove comprehensive indexes."""
    # Payment methods
    op.drop_index('ix_payment_methods_is_default', table_name='payment_methods')
    op.drop_index('ix_payment_methods_team_id', table_name='payment_methods')
    
    # Audit logs
    op.drop_index('ix_audit_logs_target', table_name='audit_logs')
    op.drop_index('ix_audit_logs_created_at', table_name='audit_logs')
    op.drop_index('ix_audit_logs_action', table_name='audit_logs')
    op.drop_index('ix_audit_logs_target_type', table_name='audit_logs')
    op.drop_index('ix_audit_logs_admin_user_id', table_name='audit_logs')
    
    # User settings
    op.drop_index('ix_user_settings_user_id', table_name='user_settings')
    
    # Usage logs
    op.drop_index('ix_usage_logs_team_action_created', table_name='usage_logs')
    op.drop_index('ix_usage_logs_created_at', table_name='usage_logs')
    op.drop_index('ix_usage_logs_action', table_name='usage_logs')
    op.drop_index('ix_usage_logs_job_id', table_name='usage_logs')
    op.drop_index('ix_usage_logs_team_id', table_name='usage_logs')
    
    # Invoices
    op.drop_index('ix_invoices_created_at', table_name='invoices')
    op.drop_index('ix_invoices_period_end', table_name='invoices')
    op.drop_index('ix_invoices_period_start', table_name='invoices')
    op.drop_index('ix_invoices_status', table_name='invoices')
    op.drop_index('ix_invoices_team_id', table_name='invoices')
    
    # Credit purchases
    op.drop_index('ix_credit_purchases_created_at', table_name='credit_purchases')
    op.drop_index('ix_credit_purchases_team_id', table_name='credit_purchases')
    
    # Subscriptions
    op.drop_index('ix_subscriptions_current_period_end', table_name='subscriptions')
    op.drop_index('ix_subscriptions_current_period_start', table_name='subscriptions')
    op.drop_index('ix_subscriptions_plan_id', table_name='subscriptions')
    op.drop_index('ix_subscriptions_status', table_name='subscriptions')
    op.drop_index('ix_subscriptions_team_id', table_name='subscriptions')
    
    # Admin users
    op.drop_index('ix_admin_users_deleted_at', table_name='admin_users')
    op.drop_index('ix_admin_users_role', table_name='admin_users')
    op.drop_index('ix_admin_users_is_suspended', table_name='admin_users')
    op.drop_index('ix_admin_users_is_active', table_name='admin_users')
    
    # Password resets
    op.drop_index('ix_password_resets_used_at', table_name='password_resets')
    op.drop_index('ix_password_resets_expires_at', table_name='password_resets')
    op.drop_index('ix_password_resets_user_id', table_name='password_resets')
    
    # OAuth accounts
    op.drop_index('ix_oauth_accounts_provider', table_name='oauth_accounts')
    op.drop_index('ix_oauth_accounts_user_id', table_name='oauth_accounts')
    
    # Refresh tokens
    op.drop_index('ix_refresh_tokens_created_at', table_name='refresh_tokens')
    op.drop_index('ix_refresh_tokens_revoked', table_name='refresh_tokens')
    op.drop_index('ix_refresh_tokens_expires_at', table_name='refresh_tokens')
    op.drop_index('ix_refresh_tokens_user_id', table_name='refresh_tokens')
    
    # Team invitations
    op.drop_index('ix_team_invitations_accepted_at', table_name='team_invitations')
    op.drop_index('ix_team_invitations_expires_at', table_name='team_invitations')
    op.drop_index('ix_team_invitations_team_id', table_name='team_invitations')
    
    # Translation artifacts
    op.drop_index('ix_translation_artifacts_created_at', table_name='translation_artifacts')
    op.drop_index('ix_translation_artifacts_target_language', table_name='translation_artifacts')
    op.drop_index('ix_translation_artifacts_status', table_name='translation_artifacts')
    op.drop_index('ix_translation_artifacts_job_id', table_name='translation_artifacts')
    
    # Transcript edits
    op.drop_index('ix_transcript_edits_created_at', table_name='transcript_edits')
    op.drop_index('ix_transcript_edits_user_id', table_name='transcript_edits')
    op.drop_index('ix_transcript_edits_transcript_id', table_name='transcript_edits')
    
    # Transcripts
    op.drop_index('ix_transcripts_deleted_at', table_name='transcripts')
    op.drop_index('ix_transcripts_created_at', table_name='transcripts')
    op.drop_index('ix_transcripts_language', table_name='transcripts')
    op.drop_index('ix_transcripts_job_id', table_name='transcripts')
    
    # Audio assets
    op.drop_index('ix_audio_assets_deleted_at', table_name='audio_assets')
    op.drop_index('ix_audio_assets_created_at', table_name='audio_assets')
    op.drop_index('ix_audio_assets_job_id', table_name='audio_assets')
    
    # Transcription jobs
    op.drop_index('ix_transcription_jobs_deleted_at', table_name='transcription_jobs')
    op.drop_index('ix_transcription_jobs_created_at', table_name='transcription_jobs')
    op.drop_index('ix_transcription_jobs_finished_at', table_name='transcription_jobs')
    op.drop_index('ix_transcription_jobs_started_at', table_name='transcription_jobs')
    op.drop_index('ix_transcription_jobs_team_status', table_name='transcription_jobs')
    op.drop_index('ix_transcription_jobs_status', table_name='transcription_jobs')
    op.drop_index('ix_transcription_jobs_team_id', table_name='transcription_jobs')
    
    # Team members
    op.drop_index('ix_team_members_role', table_name='team_members')
    op.drop_index('ix_team_members_user_id', table_name='team_members')
    op.drop_index('ix_team_members_team_id', table_name='team_members')
    
    # Teams
    op.drop_index('ix_teams_created_at', table_name='teams')
    op.drop_index('ix_teams_deleted_at', table_name='teams')
    op.drop_index('ix_teams_stripe_subscription_id', table_name='teams')
    op.drop_index('ix_teams_stripe_customer_id', table_name='teams')
    op.drop_index('ix_teams_is_suspended', table_name='teams')
    op.drop_index('ix_teams_plan', table_name='teams')
    
    # Users
    op.drop_index('ix_users_verification_token', table_name='users')
    op.drop_index('ix_users_deleted_at', table_name='users')
    op.drop_index('ix_users_is_suspended', table_name='users')
    op.drop_index('ix_users_is_active', table_name='users')
    op.drop_index('ix_users_is_verified', table_name='users')
