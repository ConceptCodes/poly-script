import { useEffect, useState } from "react";
import { apiFetch } from "../../lib/api";
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from "@poly/ui";
import { Button } from "@poly/ui";
import { Badge } from "@poly/ui";
import { Link } from "react-router-dom";

interface UsageData {
  plan: string;
  monthly_upload_count: number;
  monthly_limit: number | "inf";
  extra_credits: number;
}

export default function UploadPage() {
  const [usage, setUsage] = useState<UsageData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchUsage() {
      try {
        const data = await apiFetch("/billing/usage");
        setUsage(data);
      } catch (err) {
        console.error("Failed to fetch usage", err);
      } finally {
        setLoading(false);
      }
    }
    fetchUsage();
  }, []);

  const isLimitReached = usage 
    ? (usage.monthly_limit !== "inf" && usage.monthly_upload_count >= (usage.monthly_limit as number) && usage.extra_credits <= 0)
    : false;

  if (loading) return <div className="p-6 text-center text-muted-foreground italic">Checking limits...</div>;

  return (
    <div className="container mx-auto p-6 max-w-2xl space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Upload Audio</h1>
        {usage && (
          <Badge variant="outline">
            {usage.plan} Plan: {usage.monthly_upload_count} / {usage.monthly_limit === "inf" ? "∞" : usage.monthly_limit}
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
              Upgrade your plan to STANDARD or PRO to get more uploads, or purchase extra credits to continue.
            </p>
          </CardContent>
          <CardFooter className="flex space-x-4">
            <Button asChild>
              <Link to="/billing">Upgrade Plan</Link>
            </Button>
            {usage?.plan === 'FREE' && (
              <Button variant="outline" asChild>
                <Link to="/billing">Buy Credits</Link>
              </Button>
            )}
          </CardFooter>
        </Card>
      )}

      <Card className={isLimitReached ? "opacity-50 pointer-events-none" : ""}>
        <CardHeader>
          <CardTitle>File Upload</CardTitle>
          <CardDescription>Select an audio file to transcribe.</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="border-2 border-dashed rounded-lg p-12 text-center hover:bg-muted/50 transition-colors cursor-pointer">
            <p className="text-muted-foreground">Drag and drop audio file here, or click to select</p>
            <input type="file" className="hidden" disabled={isLimitReached} />
          </div>
        </CardContent>
        <CardFooter className="flex justify-end">
          <Button disabled={isLimitReached}>Upload & Process</Button>
        </CardFooter>
      </Card>
    </div>
  );
}
