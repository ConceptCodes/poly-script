import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@poly/ui/select";

interface LanguageFilterProps {
  value: string | undefined;
  onChange: (value: string | undefined) => void;
}

const LANGUAGES = [
  { code: "en", name: "English" },
  { code: "de", name: "German" },
  { code: "es", name: "Spanish" },
  { code: "fr", name: "French" },
  { code: "ja", name: "Japanese" },
  { code: "zh", name: "Chinese" },
];

export function LanguageFilter({ value, onChange }: LanguageFilterProps) {
  return (
    <Select value={value || ""} onValueChange={(v) => onChange(v || undefined)}>
      <SelectTrigger className="w-[150px]">
        <SelectValue placeholder="All Languages" />
      </SelectTrigger>
      <SelectContent>
        <SelectItem value="">All Languages</SelectItem>
        {LANGUAGES.map((lang) => (
          <SelectItem key={lang.code} value={lang.code}>
            {lang.name}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}
