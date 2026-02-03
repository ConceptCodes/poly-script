import { Card, CardContent, CardDescription, CardHeader, CardTitle, Progress } from "@poly/ui";

interface UsageCardProps {
  monthlyUploadCount: number;
  monthlyLimit: number | "inf";
  extraCredits: number;
}

export function UsageCard({ monthlyUploadCount, monthlyLimit, extraCredits }: UsageCardProps) {
  const isInfinite =
    monthlyLimit === "inf" || (typeof monthlyLimit === "number" && monthlyLimit === Infinity);
  const percentage = isInfinite
    ? 0
    : Math.min((monthlyUploadCount / (monthlyLimit as number)) * 100, 100);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Usage</CardTitle>
        <CardDescription>Your current usage for this month.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span>Monthly Uploads</span>
            <span>
              {monthlyUploadCount} / {isInfinite ? "∞" : monthlyLimit}
            </span>
          </div>
          {!isInfinite && <Progress value={percentage} className="h-2" />}
        </div>

        <div className="pt-4 border-t">
          <div className="flex justify-between items-center text-sm">
            <span>Extra Credits</span>
            <span className="font-bold text-lg">{extraCredits}</span>
          </div>
          <p className="text-xs text-muted-foreground mt-1">
            Extra credits are used when you exceed your monthly limit.
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
