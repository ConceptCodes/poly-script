import { Button } from "@poly/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from "@poly/ui/card";

interface PlanLimitCardProps {
  monthlyUploadCount: number;
  monthlyLimit: number;
  extraCredits: number;
  plan: string;
  onUpgrade: () => void;
  onBuyCredits: () => void;
}

export function PlanLimitCard({
  monthlyUploadCount,
  monthlyLimit,
  extraCredits,
  plan,
  onUpgrade,
  onBuyCredits,
}: PlanLimitCardProps) {
  const limitText = monthlyLimit === Infinity ? "∞" : monthlyLimit;

  return (
    <Card className="border-destructive bg-destructive/10">
      <CardHeader>
        <CardTitle className="text-destructive">Upload Limit Reached</CardTitle>
        <CardDescription>
          You have used all your monthly uploads and have no extra credits.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-sm">Monthly uploads:</span>
            <span className="text-2xl font-bold">
              {monthlyUploadCount} / {limitText}
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm">Extra credits:</span>
            <span className="text-2xl font-bold">{extraCredits}</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm">Current plan:</span>
            <span className="text-2xl font-bold">{plan}</span>
          </div>
        </div>
        <p className="text-sm">
          Upgrade your plan to STANDARD or PRO to get more uploads, or purchase extra
          credits to continue.
        </p>
      </CardContent>
      <CardFooter className="flex space-x-4">
        <Button variant="destructive" onClick={onUpgrade}>
          Upgrade Plan
        </Button>
        {plan === "FREE" && (
          <Button variant="outline" onClick={onBuyCredits}>
            Buy Credits
          </Button>
        )}
      </CardFooter>
    </Card>
  );
}
