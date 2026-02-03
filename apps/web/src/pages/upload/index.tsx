import { Card, CardContent } from "@poly/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@poly/ui/tabs";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import type { z } from "zod";
import { usePricing, useUsage } from "../../hooks/useBilling";
import { useTeamSettings } from "../../hooks/useTeamSettings";
import { api } from "../../lib/api";
import { AdvancedOptions } from "./components/AdvancedOptions";
import { PlanLimitCard } from "./components/cards/PlanLimitCard";
import { TeamLimitCard } from "./components/cards/TeamLimitCard";
import { UploadDropzone } from "./components/UploadDropzone";
import { UploadHero } from "./components/UploadHero";
import { UrlInput } from "./components/UrlInput";
import type { uploadOptionsSchema } from "./schemas";

const LANGUAGES = [
  { code: "en", label: "English" },
  { code: "de", label: "German" },
  { code: "es", label: "Spanish" },
  { code: "fr", label: "French" },
  { code: "jp", label: "Japanese" },
];

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

  const handleUrlChange = (value: string) => {
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

        const data = await api.createJob(formData);
        navigate(`/jobs/${data.job_id}/live`);
      } else {
        const urlValidationError = validateUrl(urlInput);
        if (urlValidationError) {
          setUrlError(urlValidationError);
          setIsSubmitting(false);
          return;
        }

        const data = await api.createJobFromUrl(urlInput, {
          language: values.language || undefined,
          engine: values.engine || undefined,
          timestamps: values.timestamps,
          diarization: values.diarization,
          target_language: values.target_language || undefined,
        });
        navigate(`/jobs/${data.job_id}/live`);
      }
    } catch (error: unknown) {
      const apiError = error as { status?: number };
      if (apiError.status === 402) {
        navigate("/billing?reason=limit_reached");
      } else {
        console.error("Upload error:", error);
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  if (loading) {
    return <div className="p-6 text-center text-muted-foreground">Loading...</div>;
  }

  const uploadDisabled = isLimitReached || isMemberLimitReached || isSubmitting;

  return (
    <div className="container mx-auto p-6 max-w-2xl space-y-8">
      <UploadHero uploadMode={uploadMode} />

      {isLimitReached && usage && (
        <PlanLimitCard
          monthlyUploadCount={usage.monthly_upload_count}
          monthlyLimit={usage.monthly_limit as number}
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

      <Card
        className={`precision-card smooth-transition ${
          uploadDisabled ? "opacity-50 pointer-events-none" : ""
        }`}
      >
        <CardContent className="p-6 space-y-6">
          <Tabs value={uploadMode} onValueChange={(v) => setUploadMode(v as "file" | "url")}>
            <TabsList className="grid w-full grid-cols-2 h-12 bg-muted/30 p-1 rounded-xl">
              <TabsTrigger
                value="file"
                className="data-[state=active]:bg-background data-[state=active]:shadow-sm rounded-lg smooth-transition"
              >
                Upload File
              </TabsTrigger>
              <TabsTrigger
                value="url"
                className="data-[state=active]:bg-background data-[state=active]:shadow-sm rounded-lg smooth-transition"
              >
                From URL
              </TabsTrigger>
            </TabsList>

            <TabsContent value="file" className="mt-6 animate-fade-in-up">
              <UploadDropzone onFileSelected={handleFileSelected} disabled={uploadDisabled} />
            </TabsContent>

            <TabsContent value="url" className="mt-6 animate-fade-in-up">
              <UrlInput
                value={urlInput}
                onChange={handleUrlChange}
                error={urlError}
                disabled={uploadDisabled}
              />
            </TabsContent>
          </Tabs>

          <div className="animate-fade-in-up" style={{ animationDelay: "0.1s" }}>
            <AdvancedOptions
              languageLimit={typeof languageLimit === "number" ? languageLimit : undefined}
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
