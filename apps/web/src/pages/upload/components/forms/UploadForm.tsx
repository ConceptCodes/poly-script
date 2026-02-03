import { Button } from "@poly/ui/button";
import { Label } from "@poly/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@poly/ui/select";
import { Switch } from "@poly/ui/switch";
import { useForm } from "@tanstack/react-form";
import type { z } from "zod";
import { LANGUAGE_OPTIONS, type UploadPageProps, type uploadOptionsSchema } from "../../schemas";

const TARGET_LANGUAGES = [
  { code: "es", name: "Spanish" },
  { code: "fr", name: "French" },
  { code: "de", name: "German" },
  { code: "it", name: "Italian" },
  { code: "pt", name: "Portuguese" },
  { code: "ru", name: "Russian" },
  { code: "ja", name: "Japanese" },
  { code: "zh", name: "Chinese" },
  { code: "ko", name: "Korean" },
  { code: "ar", name: "Arabic" },
  { code: "hi", name: "Hindi" },
  { code: "nl", name: "Dutch" },
  { code: "pl", name: "Polish" },
];

type UploadFormProps = UploadPageProps;

export function UploadForm({
  languageLimit,
  isLanguageRestricted,
  isSubmitting,
  onSubmit,
}: UploadFormProps) {
  const form = useForm<z.infer<typeof uploadOptionsSchema>>({
    defaultValues: {
      language: "",
      engine: "",
      timestamps: true,
      diarization: false,
      target_language: undefined,
    },
    onSubmit,
  });

  const sourceLanguage = form.state.values.language;
  const selectedTargetLanguage = form.state.values.target_language;
  const sourceLanguageValue = sourceLanguage && sourceLanguage.length > 0 ? sourceLanguage : "auto";
  const targetLanguageValue =
    selectedTargetLanguage && selectedTargetLanguage.length > 0 ? selectedTargetLanguage : "none";

  const shouldShowTargetLanguageOptions =
    !isLanguageRestricted || sourceLanguage !== selectedTargetLanguage;

  const getTranslationWarning = () => {
    if (selectedTargetLanguage && !shouldShowTargetLanguageOptions) {
      return "Target language translation is only available with an upgraded plan.";
    }
    if (isLanguageRestricted && selectedTargetLanguage) {
      return `Your plan allows only ${languageLimit} target language(s). Upgrade to access more.`;
    }
    return null;
  };

  return (
    <div className="space-y-6">
      {/* Source Language Selection */}
      <div className="space-y-2">
        <Label htmlFor="language">Source Language (ASR)</Label>
        <Select
          value={sourceLanguageValue}
          onValueChange={(value) =>
            form.setFieldValue("language", value === "auto" ? "" : (value ?? ""))
          }
          disabled={isSubmitting}
        >
          <SelectTrigger id="language">
            <SelectValue placeholder="Auto-detect" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value={"auto"}>Auto-detect</SelectItem>
            {LANGUAGE_OPTIONS.map((lang) => (
              <SelectItem key={lang.code} value={lang.code} disabled={isSubmitting}>
                {lang.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Target Language Selection */}
      <div className="space-y-2">
        <Label htmlFor="target_language">Target Language (Translation)</Label>
        <Select
          value={targetLanguageValue}
          onValueChange={(value) =>
            form.setFieldValue("target_language", value === "none" ? "" : (value ?? ""))
          }
          disabled={isSubmitting || !shouldShowTargetLanguageOptions}
        >
          <SelectTrigger id="target_language">
            <SelectValue placeholder="No translation" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value={"none"}>No translation</SelectItem>
            {TARGET_LANGUAGES.map((lang) => (
              <SelectItem
                key={lang.code}
                value={lang.code}
                disabled={!shouldShowTargetLanguageOptions || isSubmitting}
              >
                <div className="flex items-center justify-between">
                  <span>{lang.name}</span>
                  {isLanguageRestricted(lang.code) && (
                    <span className="text-xs text-muted-foreground ml-2">(Upgrade)</span>
                  )}
                </div>
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        {getTranslationWarning() && (
          <p className="text-sm text-yellow-600 dark:text-yellow-400 mt-2">
            {getTranslationWarning()}
          </p>
        )}
      </div>

      {/* Options */}
      <div className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="timestamps">Timestamps</Label>
          <div className="flex items-center space-x-2">
            <Switch
              id="timestamps"
              checked={form.state.values.timestamps}
              onCheckedChange={(checked) => form.setFieldValue("timestamps", checked)}
              disabled={isSubmitting}
            />
            <span className="text-sm">Include timestamps</span>
          </div>
        </div>

        <div className="space-y-2">
          <Label htmlFor="diarization">Speaker Diarization</Label>
          <div className="flex items-center space-x-2">
            <Switch
              id="diarization"
              checked={form.state.values.diarization}
              onCheckedChange={(checked) => form.setFieldValue("diarization", checked)}
              disabled={isSubmitting}
            />
            <span className="text-sm">Identify speakers</span>
          </div>
        </div>
      </div>

      {/* Submit */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          form.handleSubmit();
        }}
        className="w-full"
      >
        <Button type="submit" disabled={isSubmitting} className="w-full">
          {isSubmitting ? "Starting..." : "Start Transcription"}
        </Button>
      </form>
    </div>
  );
}
