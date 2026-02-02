import { useTranslation } from "react-i18next";
import { LanguageSwitcher as SharedLanguageSwitcher } from "@poly/ui";

const languages = [
  { code: "en", name: "English" },
  { code: "de", name: "Deutsch" },
  { code: "es", name: "Español" },
  { code: "fr", name: "Français" },
  { code: "jp", name: "日本語" },
];

export function LanguageSwitcher() {
  const { i18n } = useTranslation();

  return (
    <SharedLanguageSwitcher
      languages={languages}
      currentLanguageCode={i18n.language}
      onLanguageChange={(code) => i18n.changeLanguage(code)}
    />
  );
}
