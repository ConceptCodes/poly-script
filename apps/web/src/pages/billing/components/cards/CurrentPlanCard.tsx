import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from "@poly/ui";
import { Badge } from "@poly/ui";
import { Button } from "@poly/ui";

interface CurrentPlanCardProps {
  plan: string;
  status: string;
  cancelAtPeriodEnd?: boolean;
  onManage: () => void;
  onReactivate?: () => void;
}

export function CurrentPlanCard({ plan, status, cancelAtPeriodEnd, onManage, onReactivate }: CurrentPlanCardProps) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <div className="space-y-1">
          <CardTitle>Current Plan</CardTitle>
          <CardDescription>Manage your subscription and billing.</CardDescription>
        </div>
        <Badge variant={plan === 'PRO' ? 'default' : 'secondary'} className="text-sm font-bold">
          {plan}
        </Badge>
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold capitalize">
            {cancelAtPeriodEnd ? 'Canceling' : status}
        </div>
        <p className="text-xs text-muted-foreground mt-1">
          {cancelAtPeriodEnd 
            ? "Your subscription will end at the end of the current period."
            : `Your plan is currently ${status}.`
          }
        </p>
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
