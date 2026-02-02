import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { z } from "zod";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@poly/ui/tabs";
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from "@poly/ui/card";
import { Button } from "@poly/ui/button";
import { useUsage, usePricing } from "../../hooks/useBilling";
import { useTeamSettings } from "../../hooks/useTeamSettings";
import { UploadDropzone } from "./components/UploadDropzone";
import { UploadForm } from "./components/forms/UploadForm";
import { PlanLimitCard } from "./components/cards/PlanLimitCard";
import { TeamLimitCard } from "./components/cards/TeamLimitCard";
import { uploadOptionsSchema } from "./schemas";

const LANGUAGES = [
  { code: "en", label: "English" },
  { code: "de", label: "German" },
  { code: "es", label: "Spanish" },
  { code: "fr", label: "French" },
  { code: "jp", label: "Japanese" },
];

// URL validation regex patterns
const YOUTUBE_REGEX = /^(https?:\/\/(?:www\.)?(?:youtube\.com\/watch\?v=|youtu\.be\/)[\w-]+)$/;
const S3_REGEX = /^https?:\/\/[^\s]+\.s3[\w-]*\.amazonaws\.com\/[^\s]+$/;
const DIRECT_URL_REGEX = /^https?:\/\/[^\s]+$/;

export default function UploadPage() {
  const navigate = useNavigate();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadMode, setUploadMode] = useState<"file" | "url">("file");
  const [urlInput, setUrlInput] = useState("");
  const [urlError, setUrlError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { data: usage, isLoading: usageLoading } = useUsage();
  const { data: pricing, isLoading: pricingLoading } = usePricing();
  const { data: teamSettings, isLoading: teamSettingsLoading } = useTeamSettings();

  const loading = usageLoading || pricingLoading || teamSettingsLoading;

  const isLimitReached = usage
    ? usage.monthly_limit !== "inf" &&
      usage.monthly_upload_count >= (usage.monthly_limit as number) &&
      usage.extra_credits <= 0
    : false;

  // Team member limit check
  const memberLimit = (() => {
    if (!usage || !pricing) return "inf";
    if (Array.isArray(pricing.plans)) {
      const plan = pricing.plans.find((p) => p.plan === usage.plan);
      return plan?.limits.members ?? "inf";
    }
    return "inf";
  })();

  const memberCount = teamSettings?.members_count ?? 0;
  const isMemberLimitReached = memberLimit !== "inf" && memberCount >= memberLimit;

  const languageLimit = (() => {
    if (!usage || !pricing) return "inf";
    if (Array.isArray(pricing.plans)) {
      const plan = pricing.plans.find((p) => p.plan === usage.plan);
      return plan?.limits.languages ?? "inf";
    }
    return "inf";
  })();

  const isLanguageRestricted = (code: string) => {
    if (languageLimit === "inf") return false;
    return LANGUAGES.findIndex((l) => l.code === code) >= (languageLimit as number);
  };

  const validateUrl = (url: string): string | null => {
    if (!url.trim()) {
      return "Please enter a URL";
    }

    if (YOUTUBE_REGEX.test(url)) {
      return null;
    }

    if (S3_REGEX.test(url)) {
      return null;
    }

    if (DIRECT_URL_REGEX.test(url)) {
      return null;
    }

    return "Invalid URL. Supported: YouTube, S3, or direct HTTPS URLs.";
  };

  const handleFileSelected = (file: File) => {
    setSelectedFile(file);
  };

  const handleUrlChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setUrlInput(value);
    const error = validateUrl(value);
    setUrlError(error || "");
  };

  const handleSubmit = async (values: z.infer<typeof uploadOptionsSchema>) => {
    if (isSubmitting) return;

    setIsSubmitting(true);

    try {
      if (uploadMode === "file") {
        if (!selectedFile) {
          setIsSubmitting(false);
          return;
        }

        const formData = new FormData();
        formData.append("file", selectedFile);
        formData.append("language", values.language || "");
        formData.append("timestamps", values.timestamps.toString());
        formData.append("diarization", values.diarization.toString());
        formData.append("target_language", values.target_language || "");

        const response = await fetch("/api/v1/jobs", {
          method: "POST",
          body: formData,
        });

        if (response.ok) {
          const data = await response.json();
          navigate(`/jobs/${data.job_id}/live`);
        } else {
          const error = await response.json();
          console.error("Upload failed:", error);
        }
      } else {
        // URL submission
        const urlValidationError = validateUrl(urlInput);
        if (urlValidationError) {
          setUrlError(urlValidationError);
          setIsSubmitting(false);
          return;
        }

        const response = await fetch("/api/v1/jobs/url", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            url: urlInput,
            options: {
              language: values.language || undefined,
              engine: values.engine || undefined,
              timestamps: values.timestamps,
              diarization: values.diarization,
              target_language: values.target_language || undefined,
            },
          }),
        });

        if (response.ok) {
          const data = await response.json();
          navigate(`/jobs/${data.job_id}/live`);
        } else {
          const error = await response.json();
          console.error("URL submission failed:", error);
        }
      }
    } catch (error) {
      console.error("Upload error:", error);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (loading) {
    return <div className="p-6 text-center text-muted-foreground">Loading...</div>;
  }

  const uploadDisabled = isLimitReached || isMemberLimitReached || isSubmitting;

  return (
    <div className="container mx-auto p-6 max-w-2xl space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Upload Audio</h1>
        {usage && (
          <Button variant="outline" size="sm" onClick={() => navigate("/billing")}>
            Billing
          </Button>
        )}
      </div>

      {isLimitReached && (
        <PlanLimitCard
          monthlyUploadCount={usage.monthly_upload_count}
          monthlyLimit={usage.monthly_limit}
          extraCredits={usage.extra_credits}
          plan={usage.plan}
          onUpgrade={() => navigate("/billing")}
          onBuyCredits={() => navigate("/billing")}
        />
      )}

      {isMemberLimitReached && teamSettings && (
        <TeamLimitCard
          memberCount={memberCount}
          memberLimit={memberLimit}
          plan={usage?.plan || "FREE"}
          onUpgrade={() => navigate("/billing")}
        />
      )}

      <Card className={uploadDisabled ? "opacity-50 pointer-events-none" : ""}>
        <CardHeader>
          <CardTitle>Transcribe Audio</CardTitle>
          <CardDescription>Upload a file or provide a URL to transcribe.</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            <Tabs value={uploadMode} onValueChange={(v) => setUploadMode(v as "file" | "url")}>
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="file">Upload File</TabsTrigger>
                <TabsTrigger value="url">From URL</TabsTrigger>
              </TabsList>

              <TabsContent value="file">
                <UploadDropzone
                  onFileSelected={handleFileSelected}
                  disabled={uploadDisabled}
                />
              </TabsContent>

              <TabsContent value="url">
                <div className="space-y-4">
                  <div className="space-y-2">
                    <label htmlFor="url-input" className="text-sm font-medium">
                      Audio URL
                    </label>
                    <input
                      id="url-input"
                      type="url"
                      placeholder="https://youtube.com/watch?v=... or direct audio URL"
                      value={urlInput}
                      onChange={handleUrlChange}
                      disabled={uploadDisabled}
                      className={`w-full px-3 py-2 border rounded-md ${
                        urlError
                          ? "border-destructive focus:ring-destructive"
                          : "focus:ring-primary"
                      }`}
                    />
                    {urlError && (
                      <p className="text-sm text-destructive">{urlError}</p>
                    )}
                    <p className="text-xs text-muted-foreground">
                      Supported: YouTube URLs, S3 URLs, or direct HTTPS file URLs
                    </p>
                  </div>
                </div>
              </TabsContent>
            </Tabs>

            <UploadForm
              languageLimit={languageLimit}
              isLanguageRestricted={isLanguageRestricted}
              isSubmitting={isSubmitting}
              onSubmit={handleSubmit}
            />
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
