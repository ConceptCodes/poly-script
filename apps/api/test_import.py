try:
    from poly_core.services.auth import AuthService
    print("AuthService imported successfully!")
except Exception as e:
    print(f"Failed to import AuthService: {e}")
    import sys
    sys.exit(1)
