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

const ALL_LANGUAGES_VALUE = "__all__";

export function LanguageFilter({ value, onChange }: LanguageFilterProps) {
  const handleValueChange = (v: string) => {
    if (v === ALL_LANGUAGES_VALUE) {
      onChange(undefined);
    } else {
      onChange(v);
    }
  };

  const selectValue = value || ALL_LANGUAGES_VALUE;

  return (
    <Select value={selectValue} onValueChange={handleValueChange}>
      <SelectTrigger className="w-[150px]">
        <SelectValue placeholder="All Languages" />
      </SelectTrigger>
      <SelectContent>
        <SelectItem value={ALL_LANGUAGES_VALUE}>All Languages</SelectItem>
        {LANGUAGES.map((lang) => (
          <SelectItem key={lang.code} value={lang.code}>
            {lang.name}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}
