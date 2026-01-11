import { useForm } from "@tanstack/react-form";
import { z } from "zod";
import { Button } from "@poly/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@poly/ui/select";
import { Label } from "@poly/ui/label";
import { Switch } from "@poly/ui/switch";
import { uploadOptionsSchema } from "../schemas";

const LANGUAGES = [
  { code: "en", label: "English" },
  { code: "de", label: "German" },
  { code: "es", label: "Spanish" },
  { code: "fr", label: "French" },
  { code: "jp", label: "Japanese" },
];

interface UploadFormProps {
  languageLimit?: number;
  isLanguageRestricted: (code: string) => boolean;
  isSubmitting?: boolean;
  onSubmit: (values: z.infer<typeof uploadOptionsSchema>) => void;
}

export function UploadForm({
  languageLimit,
  isLanguageRestricted,
  isSubmitting,
  onSubmit,
}: UploadFormProps) {
  const form = useForm({
    defaultValues: {
      language: null,
      engine: null,
      timestamps: true,
      diarization: false,
    },
    onSubmit,
  });

  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <Label htmlFor="language">Language</Label>
        <Select
          value={form.state.values.language}
          onValueChange={(value) => form.setFieldValue("language", value)}
          disabled={isSubmitting}
        >
          <SelectTrigger id="language">
            <SelectValue placeholder="Auto-detect" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value={null}>Auto-detect</SelectItem>
            {LANGUAGES.map((lang) => (
              <SelectItem
                key={lang.code}
                value={lang.code}
                disabled={isLanguageRestricted(lang.code)}
              >
                {lang.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        {languageLimit && languageLimit !== "inf" && (
          <p className="text-xs text-muted-foreground">
            Your plan allows {languageLimit} language(s). Upgrade to STANDARD for all languages.
          </p>
        )}
      </div>

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

      <form.Provider>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            form.handleSubmit();
          }}
        >
          <Button
            type="submit"
            disabled={isSubmitting}
            className="w-full"
          >
            {isSubmitting ? "Starting..." : "Start Transcription"}
          </Button>
        </form>
      </form.Provider>
    </div>
  );
}
