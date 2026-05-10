import { Button } from "@poly/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@poly/ui/card";
import { Shield, Users } from "lucide-react";

interface TeamLimitCardProps {
  memberCount: number;
  memberLimit: number | "inf";
  plan: string;
  onUpgrade: () => void;
}

export function TeamLimitCard({ memberCount, memberLimit, plan, onUpgrade }: TeamLimitCardProps) {
  const limitText = memberLimit === "inf" ? "∞" : memberLimit;
  const isLimitReached = typeof memberLimit === "number" && memberCount >= memberLimit;

  if (!isLimitReached) {
    return null;
  }

  const percentage =
    typeof memberLimit === "number" && memberLimit > 0 ? (memberCount / memberLimit) * 100 : 100;

  return (
    <Card className="precision-card border-destructive/60 bg-gradient-to-br from-destructive/10 to-destructive/5 animate-fade-in-up overflow-hidden">
      <div className="absolute top-0 left-0 right-0 h-1 bg-destructive/50" />
      <CardHeader className="relative">
        <div className="flex items-start gap-3">
          <div className="p-2 rounded-lg bg-destructive/10 animate-gentle-pulse">
            <Shield className="h-5 w-5 text-destructive" />
          </div>
          <div className="flex-1">
            <CardTitle className="text-destructive">Team Member Limit</CardTitle>
            <CardDescription className="mt-1">
              Your team has reached the maximum number of members for your plan.
            </CardDescription>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="flex items-center gap-6">
          <div className="flex-1 p-4 rounded-lg bg-background/50">
            <div className="flex items-center justify-center gap-2">
              <Users className="h-8 w-8 text-destructive/60" />
              <div>
                <div className="text-3xl font-bold text-foreground">
                  {memberCount}{" "}
                  <span className="text-lg font-normal text-muted-foreground">/ {limitText}</span>
                </div>
                <div className="text-xs text-muted-foreground mt-1">Team Members</div>
              </div>
            </div>
          </div>
        </div>

        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Member usage</span>
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
          <Users className="h-4 w-4 mt-0.5 flex-shrink-0" />
          <p>
            Current plan: <span className="font-medium text-foreground">{plan}</span>
            <span className="mx-1">•</span>
            Upgrade to add more team members and collaborate seamlessly.
          </p>
        </div>
      </CardContent>
      <CardFooter className="pt-2">
        <Button
          variant="destructive"
          onClick={onUpgrade}
          className="w-full smooth-transition hover:shadow-lg hover:shadow-destructive/20"
        >
          Upgrade Plan
        </Button>
      </CardFooter>
    </Card>
  );
}
