from fastapi import Header


async def get_locale(accept_language: str | None = Header(None)) -> str:
    """
    Parse Accept-Language header and return the best matching locale.
    Simple implementation: take the first language from the header.
    Authentication dependency will overload this to prefer user profile settings.
    """
    if not accept_language:
        return "en"

    # Basic parsing: "en-US,en;q=0.9" -> "en"
    # We just want the primary tag of the first preference
    primary = accept_language.split(",")[0].strip().split(";")[0].strip()

    # Handle "en-US" -> "en" if strict match fails (simplified for now)
    # The i18n service handles fallback to 'en', so we just return the code.
    return primary
