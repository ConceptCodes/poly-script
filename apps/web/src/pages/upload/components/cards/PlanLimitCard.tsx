import { Button } from "@poly/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@poly/ui/card";
import { AlertTriangle, TrendingUp } from "lucide-react";

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
  const percentage = monthlyLimit !== Infinity ? (monthlyUploadCount / monthlyLimit) * 100 : 100;

  return (
    <Card className="precision-card border-destructive/60 bg-gradient-to-br from-destructive/10 to-destructive/5 animate-fade-in-up overflow-hidden">
      <div className="absolute top-0 left-0 right-0 h-1 bg-destructive/50" />
      <CardHeader className="relative">
        <div className="flex items-start gap-3">
          <div className="p-2 rounded-lg bg-destructive/10 animate-gentle-pulse">
            <AlertTriangle className="h-5 w-5 text-destructive" />
          </div>
          <div className="flex-1">
            <CardTitle className="text-destructive">Upload Limit Reached</CardTitle>
            <CardDescription className="mt-1">
              You've used all monthly uploads and have no extra credits remaining.
            </CardDescription>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="grid grid-cols-3 gap-4">
          <div className="text-center p-3 rounded-lg bg-background/50">
            <div className="text-2xl font-bold text-foreground">
              {monthlyUploadCount}
              <span className="text-sm font-normal text-muted-foreground ml-1">/{limitText}</span>
            </div>
            <div className="text-xs text-muted-foreground mt-1">Monthly</div>
          </div>
          <div className="text-center p-3 rounded-lg bg-background/50">
            <div className="text-2xl font-bold text-foreground">{extraCredits}</div>
            <div className="text-xs text-muted-foreground mt-1">Credits</div>
          </div>
          <div className="text-center p-3 rounded-lg bg-background/50">
            <div className="text-lg font-bold text-foreground">{plan}</div>
            <div className="text-xs text-muted-foreground mt-1">Plan</div>
          </div>
        </div>

        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Monthly usage</span>
            <span className="font-medium">{Math.round(percentage)}%</span>
          </div>
          <div className="h-2 bg-muted rounded-full overflow-hidden">
            <div
              className="h-full bg-destructive transition-all duration-500 ease-out"
              style={{ width: `${Math.min(percentage, 100)}%` }}
            />
          </div>
        </div>

        <div className="flex items-start gap-2 text-sm text-muted-foreground">
          <TrendingUp className="h-4 w-4 mt-0.5 flex-shrink-0" />
          <p>
            Upgrade to <span className="font-medium text-foreground">STANDARD</span> (25/month) or{" "}
            <span className="font-medium text-foreground">PRO</span> (unlimited) to continue
            uploading.
          </p>
        </div>
      </CardContent>
      <CardFooter className="flex gap-3 pt-2">
        <Button
          variant="destructive"
          onClick={onUpgrade}
          className="flex-1 smooth-transition hover:shadow-lg hover:shadow-destructive/20"
        >
          Upgrade Plan
        </Button>
        {plan === "FREE" && (
          <Button
            variant="outline"
            onClick={onBuyCredits}
            className="flex-1 smooth-transition border-destructive/30 hover:border-destructive/60 hover:bg-destructive/5"
          >
            Buy Credits
          </Button>
        )}
      </CardFooter>
    </Card>
  );
}
