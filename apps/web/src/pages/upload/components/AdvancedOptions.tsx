import { Button } from "@poly/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@poly/ui/card";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@poly/ui/collapsible";
import { Label } from "@poly/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@poly/ui/select";
import { Switch } from "@poly/ui/switch";
import { useForm } from "@tanstack/react-form";
import { ChevronDown, ChevronUp, Clock, Globe, Settings, Users } from "lucide-react";
import { useState } from "react";
import type { z } from "zod";
import { LANGUAGE_OPTIONS, type UploadFormValues, type uploadOptionsSchema } from "../schemas";

const TARGET_LANGUAGES = [
  { code: "es", name: "Spanish", flag: "🇪🇸" },
  { code: "fr", name: "French", flag: "🇫🇷" },
  { code: "de", name: "German", flag: "🇩🇪" },
  { code: "it", name: "Italian", flag: "🇮🇹" },
  { code: "pt", name: "Portuguese", flag: "🇵🇹" },
  { code: "ru", name: "Russian", flag: "🇷🇺" },
  { code: "ja", name: "Japanese", flag: "🇯🇵" },
  { code: "zh", name: "Chinese", flag: "🇨🇳" },
  { code: "ko", name: "Korean", flag: "🇰🇷" },
  { code: "ar", name: "Arabic", flag: "🇸🇦" },
  { code: "hi", name: "Hindi", flag: "🇮🇳" },
  { code: "nl", name: "Dutch", flag: "🇳🇱" },
  { code: "pl", name: "Polish", flag: "🇵🇱" },
];

interface AdvancedOptionsProps {
  languageLimit?: number | "inf";
  isLanguageRestricted: (code: string) => boolean;
  isSubmitting: boolean;
  onSubmit: (values: UploadFormValues) => void;
}

export function AdvancedOptions({
  languageLimit,
  isLanguageRestricted,
  isSubmitting,
  onSubmit,
}: AdvancedOptionsProps) {
  const [isAdvancedOpen, setIsAdvancedOpen] = useState(false);
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
      return "Target language translation requires an upgraded plan.";
    }
    if (isLanguageRestricted(selectedTargetLanguage)) {
      return `Your plan allows ${languageLimit} target language(s). Upgrade for more.`;
    }
    return null;
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 gap-3">
        <div className="space-y-2">
          <Label htmlFor="language" className="text-sm font-medium text-foreground">
            <Globe className="inline h-4 w-4 mr-1.5" />
            Source Language
          </Label>
          <Select
            value={sourceLanguageValue}
            onValueChange={(value) => form.setFieldValue("language", value === "auto" ? "" : value)}
          >
            <SelectTrigger id="language" disabled={isSubmitting}>
              <SelectValue placeholder="Auto-detect" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="auto">Auto-detect</SelectItem>
              {LANGUAGE_OPTIONS.map((lang) => (
                <SelectItem key={lang.code} value={lang.code}>
                  {lang.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <Label htmlFor="target_language" className="text-sm font-medium text-foreground">
            <Globe className="inline h-4 w-4 mr-1.5" />
            Translate to
          </Label>
          <Select
            value={targetLanguageValue}
            onValueChange={(value) =>
              form.setFieldValue("target_language", value === "none" ? "" : value)
            }
          >
            <SelectTrigger
              id="target_language"
              disabled={isSubmitting || !shouldShowTargetLanguageOptions}
            >
              <SelectValue placeholder="No translation" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="none">No translation</SelectItem>
              {TARGET_LANGUAGES.map((lang) => (
                <SelectItem
                  key={lang.code}
                  value={lang.code}
                  disabled={isLanguageRestricted(lang.code)}
                >
                  {lang.flag} {lang.name}
                  {isLanguageRestricted(lang.code) && " (Upgrade)"}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          {getTranslationWarning() && (
            <p className="text-xs text-amber-600 dark:text-amber-400 flex items-center gap-1">
              <Settings className="h-3 w-3" />
              {getTranslationWarning()}
            </p>
          )}
        </div>
      </div>

      <Collapsible open={isAdvancedOpen} onOpenChange={setIsAdvancedOpen}>
        <CollapsibleTrigger asChild>
          <Button
            type="button"
            variant="ghost"
            className="w-full justify-between text-muted-foreground hover:text-foreground hover:bg-muted/50 smooth-transition"
            disabled={isSubmitting}
          >
            <span className="flex items-center gap-2 text-sm font-medium">
              <Settings className="h-4 w-4" />
              Advanced Options
            </span>
            {isAdvancedOpen ? (
              <ChevronUp className="h-4 w-4 smooth-transition" />
            ) : (
              <ChevronDown className="h-4 w-4 smooth-transition" />
            )}
          </Button>
        </CollapsibleTrigger>

        <CollapsibleContent className="mt-4 animate-fade-in-up">
          <Card className="precision-card">
            <CardHeader className="pb-3">
              <CardTitle className="text-base font-medium flex items-center gap-2">
                <Settings className="h-4 w-4 text-muted-foreground" />
                Transcription Settings
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between p-3 rounded-lg bg-muted/30">
                <div className="flex items-center gap-3">
                  <div className="flex items-center justify-center h-9 w-9 rounded-lg bg-primary/10">
                    <Clock className="h-5 w-5 text-primary" />
                  </div>
                  <div className="space-y-0.5">
                    <Label htmlFor="timestamps" className="text-sm font-medium">
                      Timestamps
                    </Label>
                    <p className="text-xs text-muted-foreground">
                      Include segment-level timestamps
                    </p>
                  </div>
                </div>
                <Switch
                  id="timestamps"
                  checked={form.state.values.timestamps}
                  onCheckedChange={(checked) => form.setFieldValue("timestamps", checked)}
                  disabled={isSubmitting}
                  className="precision-switch"
                />
              </div>

              <div className="flex items-center justify-between p-3 rounded-lg bg-muted/30">
                <div className="flex items-center gap-3">
                  <div className="flex items-center justify-center h-9 w-9 rounded-lg bg-accent/10">
                    <Users className="h-5 w-5 text-accent" />
                  </div>
                  <div className="space-y-0.5">
                    <Label htmlFor="diarization" className="text-sm font-medium">
                      Speaker Diarization
                    </Label>
                    <p className="text-xs text-muted-foreground">Identify different speakers</p>
                  </div>
                </div>
                <Switch
                  id="diarization"
                  checked={form.state.values.diarization}
                  onCheckedChange={(checked) => form.setFieldValue("diarization", checked)}
                  disabled={isSubmitting}
                  className="precision-switch"
                />
              </div>
            </CardContent>
          </Card>
        </CollapsibleContent>
      </Collapsible>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          form.handleSubmit();
        }}
        className="w-full"
      >
        <Button
          type="submit"
          disabled={isSubmitting}
          className="w-full h-12 text-base font-medium precision-gradient shadow-lg shadow-primary/20 hover:shadow-xl hover:shadow-primary/30 smooth-transition"
        >
          {isSubmitting ? "Processing..." : "Start Transcription"}
        </Button>
      </form>
    </div>
  );
}
