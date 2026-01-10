import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
  CardFooter,
  Button,
  Badge,
  Select,
  SelectTrigger,
  SelectValue,
  SelectContent,
  SelectItem,
} from "@poly/ui";
import { Link } from "react-router-dom";
import { useState } from "react";
import { useUsage, usePricing } from "../../hooks/useBilling";
import type { PricingPlan } from "../../types/api";

const LANGUAGES = [
  { code: "en", label: "English" },
  { code: "de", label: "German" },
  { code: "es", label: "Spanish" },
  { code: "fr", label: "French" },
  { code: "jp", label: "Japanese" },
];

export function UploadPage() {
  const [selectedLanguage, setSelectedLanguage] = useState("en");

  // Queries
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
      const plan = pricing.plans.find((p: PricingPlan) => p.plan === usage.plan);
      return plan?.limits.languages ?? "inf";
    }
    return "inf";
  })();

  const isLanguageRestricted = (code: string) => {
    if (languageLimit === "inf") return false;
    return LANGUAGES.findIndex((l) => l.code === code) >= (languageLimit as number);
  };

  const selectedLanguageRestricted = isLanguageRestricted(selectedLanguage);

  if (loading)
    return <div className="p-6 text-center text-muted-foreground italic">Checking limits...</div>;

  return (
    <div className="container mx-auto p-6 max-w-2xl space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Upload Audio</h1>
        {usage && (
          <Badge variant="outline">
            {usage.plan} Plan: {usage.monthly_upload_count} /{" "}
            {usage.monthly_limit === "inf" ? "∞" : usage.monthly_limit}
          </Badge>
        )}
      </div>

      {isLimitReached && (
        <Card className="border-destructive bg-destructive/10">
          <CardHeader>
            <CardTitle className="text-destructive">Upload Limit Reached</CardTitle>
            <CardDescription>
              You have used all your monthly uploads and have no extra credits.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm">
              Upgrade your plan to STANDARD or PRO to get more uploads, or purchase extra credits to
              continue.
            </p>
          </CardContent>
          <CardFooter className="flex space-x-4">
            <Button asChild>
              <Link to="/billing">Upgrade Plan</Link>
            </Button>
            {usage?.plan === "FREE" && (
              <Button variant="outline" asChild>
                <Link to="/billing">Buy Credits</Link>
              </Button>
            )}
          </CardFooter>
        </Card>
      )}

      {selectedLanguageRestricted && (
        <Card className="border-amber-500 bg-amber-50">
          <CardHeader>
            <CardTitle className="text-amber-700">Language Not Available</CardTitle>
            <CardDescription>
              Your current plan doesn't include this language. Upgrade to unlock all languages.
            </CardDescription>
          </CardHeader>
          <CardFooter className="flex space-x-4">
            <Button asChild>
              <Link to="/billing">Upgrade Plan</Link>
            </Button>
          </CardFooter>
        </Card>
      )}

      <Card className={isLimitReached ? "opacity-50 pointer-events-none" : ""}>
        <CardHeader>
          <CardTitle>File Upload</CardTitle>
          <CardDescription>Select an audio file to transcribe.</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-2 mb-6">
            <label className="text-sm font-medium">Language</label>
            <Select value={selectedLanguage} onValueChange={setSelectedLanguage}>
              <SelectTrigger>
                <SelectValue placeholder="Select language" />
              </SelectTrigger>
              <SelectContent>
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
            {languageLimit !== "inf" && (
              <p className="text-xs text-muted-foreground">
                Your plan allows {languageLimit} languages.
              </p>
            )}
          </div>
          <div className="border-2 border-dashed rounded-lg p-12 text-center hover:bg-muted/50 transition-colors cursor-pointer">
            <p className="text-muted-foreground">
              Drag and drop audio file here, or click to select
            </p>
            <input
              type="file"
              className="hidden"
              disabled={isLimitReached || selectedLanguageRestricted}
            />
          </div>
        </CardContent>
        <CardFooter className="flex justify-end">
          <Button disabled={isLimitReached || selectedLanguageRestricted}>Upload & Process</Button>
        </CardFooter>
      </Card>
    </div>
  );
}
