import json
import os
from typing import Dict, Any, Optional


class I18nService:
    def __init__(self, locales_dir: str):
        self.locales_dir = locales_dir
        self._cache: Dict[str, Dict[str, Any]] = {}

    def _load_locale(self, locale: str) -> Dict[str, Any]:
        if locale in self._cache:
            return self._cache[locale]

        file_path = os.path.join(self.locales_dir, f"{locale}.json")
        if not os.path.exists(file_path):
            # Fallback to English if not found
            if locale == "en":
                return {}
            return self._load_locale("en")

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            self._cache[locale] = data
            return data

    def t(self, key: str, locale: str = "en", **kwargs: Any) -> str:
        data = self._load_locale(locale)
        keys = key.split(".")

        value = data
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                # Fallback to English if key missing in current locale
                if locale != "en":
                    return self.t(key, locale="en", **kwargs)
                return key

        if not isinstance(value, str):
            return key

        return value.format(**kwargs)


# Instance will be created with proper path at app startup
i18n = None
