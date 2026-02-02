import * as React from "react";
import { Globe } from "lucide-react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../ui/select";

export interface Language {
  code: string;
  name: string;
}

export interface LanguageSwitcherProps {
  languages: Language[];
  currentLanguageCode: string;
  onLanguageChange: (code: string) => void;
  className?: string;
  showIcon?: boolean;
}

export function LanguageSwitcher({
  languages,
  currentLanguageCode,
  onLanguageChange,
  className,
  showIcon = true,
}: LanguageSwitcherProps) {
  const currentLanguage = languages.find(
    (lang) => lang.code === currentLanguageCode,
  );

  return (
    <Select value={currentLanguageCode} onValueChange={onLanguageChange}>
      <SelectTrigger className={className || "w-[140px]"}>
        {showIcon && <Globe className="mr-2 h-4 w-4" />}
        <SelectValue placeholder={currentLanguage?.name} />
      </SelectTrigger>
      <SelectContent>
        {languages.map((language) => (
          <SelectItem key={language.code} value={language.code}>
            {language.name}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}
