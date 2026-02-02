import { Button } from "@poly/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from "@poly/ui/card";
import { Users } from "lucide-react";

interface TeamLimitCardProps {
  memberCount: number;
  memberLimit: number | "inf";
  plan: string;
  onUpgrade: () => void;
}

export function TeamLimitCard({
  memberCount,
  memberLimit,
  plan,
  onUpgrade,
}: TeamLimitCardProps) {
  const limitText = memberLimit === Infinity ? "∞" : memberLimit;
  const isLimitReached = memberLimit !== "inf" && memberCount >= memberLimit;

  if (!isLimitReached) {
    return null;
  }

  return (
    <Card className="border-destructive bg-destructive/10">
      <CardHeader>
        <CardTitle className="text-destructive flex items-center gap-2">
          <Users className="h-5 w-5" />
          Team Member Limit Reached
        </CardTitle>
        <CardDescription>
          Your team has reached the maximum number of members for your plan.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-sm">Team members:</span>
            <span className="text-2xl font-bold">
              {memberCount} / {limitText}
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm">Current plan:</span>
            <span className="text-2xl font-bold">{plan}</span>
          </div>
        </div>
        <p className="text-sm">
          Upgrade your plan to STANDARD or PRO to add more team members.
        </p>
      </CardContent>
      <CardFooter>
        <Button variant="destructive" onClick={onUpgrade}>
          Upgrade Plan
        </Button>
      </CardFooter>
    </Card>
  );
}
