#!/usr/bin/env python3
"""Create a SUPER_ADMIN admin user via AdminAuthService.

Inputs:
- Email, password, full_name via environment variables:
  ADMIN_EMAIL, ADMIN_PASSWORD, ADMIN_FULL_NAME
- Or via CLI:
  --email, --password, --full-name

Behavior:
- Creates a SUPER_ADMIN admin user if one doesn't exist.
- If an admin with the provided email already exists, exits with a non-zero code and a helpful message.
- Uses the AdminAuthService from the core package and reuses the existing DB session factory.
"""

import sys
import os
import argparse
import pathlib
import uuid
import importlib

def _setup_python_path():
    # Support running this script from repo root without installing packages
    script_dir = pathlib.Path(__file__).resolve()
    # Path to core package (where AdminAuthService lives)
    core_pkg = script_dir.parent.parent.parent / "packages" / "core"
    if core_pkg.exists():
        sys.path.insert(0, str(core_pkg))
    # Path to db (db layer with get_db_session)
    db_path = script_dir.parent.parent.parent / "packages" / "storage" / "db"
    if db_path.exists():
        sys.path.insert(0, str(db_path))

def _parse_args():
    ap = argparse.ArgumentParser(description="Create a SUPER_ADMIN user via AdminAuthService")
    ap.add_argument("--email", help="Admin email address")
    ap.add_argument("--password", help="Admin password")
    ap.add_argument("--full-name", dest="full_name", help="Admin full name")
    # Allow overriding via environment variables if not passed on CLI
    return ap.parse_args()

def _load_inputs():
    # CLI first
    args = _parse_args()
    email = args.email
    password = args.password
    full_name = args.full_name

    # Fallback to environment variables if not provided
    if not email:
        email = os.environ.get("ADMIN_EMAIL")
    if not password:
        password = os.environ.get("ADMIN_PASSWORD")
    if not full_name:
        full_name = os.environ.get("ADMIN_FULL_NAME")

    if not email or not password or not full_name:
        print("Error: email, password and full_name are required (via CLI or ADMIN_* env vars).", file=sys.stderr)
        sys.exit(2)

    return email, password, full_name

def main():
    _setup_python_path()
    email, password, full_name = _load_inputs()

    # Import after adjusting sys.path
    try:
        # AdminAuthService is exposed via the core package
        from poly_db.database import get_db_session
        from poly_core.services.admin_auth import AdminAuthService
    except Exception as exc:
        print(f"Error importing admin auth dependencies: {exc}", file=sys.stderr)
        sys.exit(3)

    # Admin secret and token expiry (admin tokens are separate from user tokens)
    admin_jwt_secret = os.environ.get("ADMIN_JWT_SECRET") or os.environ.get("JWT_SECRET")
    if not admin_jwt_secret:
        print("Error: ADMIN_JWT_SECRET environment variable is not set.", file=sys.stderr)
        sys.exit(4)

    admin_jwt_expiry = os.environ.get("ADMIN_JWT_EXPIRY_MINUTES")
    try:
        jwt_expiry_minutes = int(admin_jwt_expiry) if admin_jwt_expiry else 60
    except ValueError:
        print("Error: ADMIN_JWT_EXPIRY_MINUTES must be an integer.", file=sys.stderr)
        sys.exit(5)

    # Create admin using a dedicated DB session
    with get_db_session() as db_session:
        svc = AdminAuthService(db_session, admin_jwt_secret, jwt_expiry_minutes)
        try:
            created = svc.create_admin_user(email=email, password=password, full_name=full_name, role="SUPER_ADMIN")
            print(f"SUCCESS: Admin created: {created.email} (id={created.id}, role={created.role})")
            sys.exit(0)
        except ValueError as ve:
            print(f"ERROR: {ve}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"UNEXPECTED ERROR: {e}", file=sys.stderr)
            sys.exit(9)

if __name__ == "__main__":
    main()
