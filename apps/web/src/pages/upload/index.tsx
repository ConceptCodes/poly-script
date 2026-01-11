import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { z } from "zod";
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from "@poly/ui/card";
import { Button } from "@poly/ui/button";
import { useUsage, usePricing } from "../../hooks/useBilling";
import UploadDropzone from "./components/UploadDropzone";
import UploadForm from "./components/forms/UploadForm";
import PlanLimitCard from "./components/cards/PlanLimitCard";
import { uploadOptionsSchema } from "./schemas";

const LANGUAGES = [
  { code: "en", label: "English" },
  { code: "de", label: "German" },
  { code: "es", label: "Spanish" },
  { code: "fr", label: "French" },
  { code: "jp", label: "Japanese" },
];

export default function UploadPage() {
  const navigate = useNavigate();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { data: usage, isLoading: usageLoading } = useUsage();
  const { data: pricing, isLoading: pricingLoading } = usePricing();

  const loading = usageLoading || pricingLoading;

  const isLimitReached = usage
    ? usage.monthly_limit !== "inf" &&
      usage.monthly_upload_count >= (usage.monthly_limit as number) &&
      usage.extra_credits <= 0
    : false;

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

  const handleFileSelected = (file: File) => {
    setSelectedFile(file);
  };

  const handleSubmit = async (values: z.infer<typeof uploadOptionsSchema>) => {
    if (!selectedFile) return;
    if (isSubmitting) return;

    setIsSubmitting(true);

    try {
      const formData = new FormData();
      formData.append("file", selectedFile);
      formData.append("language", values.language || "");
      formData.append("timestamps", values.timestamps.toString());
      formData.append("diarization", values.diarization.toString());

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
    } catch (error) {
      console.error("Upload error:", error);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (loading) {
    return <div className="p-6 text-center text-muted-foreground">Loading...</div>;
  }

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

      <Card className={isLimitReached ? "opacity-50 pointer-events-none" : ""}>
        <CardHeader>
          <CardTitle>File Upload</CardTitle>
          <CardDescription>Select an audio file to transcribe.</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            <UploadDropzone
              onFileSelected={handleFileSelected}
              disabled={isLimitReached || isSubmitting}
            />

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
