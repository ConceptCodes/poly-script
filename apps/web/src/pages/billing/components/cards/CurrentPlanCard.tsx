import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from "@poly/ui";
import { Badge } from "@poly/ui";
import { Button } from "@poly/ui";

interface CurrentPlanCardProps {
  plan: string;
  status: string;
  cancelAtPeriodEnd?: boolean;
  currentPeriodStart?: string;
  currentPeriodEnd?: string;
  planPrice?: number;
  onManage: () => void;
  onReactivate?: () => void;
}

export function CurrentPlanCard({
  plan,
  status,
  cancelAtPeriodEnd,
  currentPeriodStart,
  currentPeriodEnd,
  planPrice,
  onManage,
  onReactivate,
}: CurrentPlanCardProps) {
  const periodLabel =
    currentPeriodStart && currentPeriodEnd
      ? `${new Date(currentPeriodStart).toLocaleDateString()} - ${new Date(
          currentPeriodEnd
        ).toLocaleDateString()}`
      : null;
  const nextBillingDate = currentPeriodEnd
    ? new Date(currentPeriodEnd).toLocaleDateString()
    : null;
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <div className="space-y-1">
          <CardTitle>Current Plan</CardTitle>
          <CardDescription>Manage your subscription and billing.</CardDescription>
        </div>
        <Badge variant={plan === "PRO" ? "default" : "secondary"} className="text-sm font-bold">
          {plan}
        </Badge>
      </CardHeader>
      <CardContent>
        {planPrice !== undefined && (
          <div className="text-sm text-muted-foreground mb-2">
            ${planPrice}/month
          </div>
        )}
        <div className="text-2xl font-bold capitalize">
          {cancelAtPeriodEnd ? "Canceling" : status}
        </div>
        <p className="text-xs text-muted-foreground mt-1">
          {cancelAtPeriodEnd
            ? "Your subscription will end at the end of the current period."
            : `Your plan is currently ${status}.`}
        </p>
        {periodLabel && (
          <p className="text-xs text-muted-foreground mt-2">
            Current period: {periodLabel}
          </p>
        )}
        {plan !== "FREE" && nextBillingDate && (
          <p className="text-xs text-muted-foreground mt-1">
            Next billing date: {nextBillingDate}
          </p>
        )}
      </CardContent>
      <CardFooter className="gap-2">
        <Button onClick={onManage} variant="outline" className="w-full">
          Manage Billing
        </Button>
        {cancelAtPeriodEnd && onReactivate && (
          <Button onClick={onReactivate} variant="default" className="w-full">
            Reactivate
          </Button>
        )}
      </CardFooter>
    </Card>
  );
}
