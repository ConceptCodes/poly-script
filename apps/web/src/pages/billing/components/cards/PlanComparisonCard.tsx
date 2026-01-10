import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
  CardFooter,
  Button,
} from "@poly/ui";

interface PlanComparisonCardProps {
  currentPlan: string;
  onUpgrade: (plan: string) => void;
  isLoading?: boolean;
}

export function PlanComparisonCard({ currentPlan, onUpgrade, isLoading }: PlanComparisonCardProps) {
  return (
    <section className="space-y-4">
      <h2 className="text-2xl font-semibold">Available Plans</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className={currentPlan === "FREE" ? "border-primary" : ""}>
          <CardHeader>
            <CardTitle>Free</CardTitle>
            <CardDescription>Perfect for getting started.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              $0<span className="text-sm font-normal text-muted-foreground">/mo</span>
            </div>
            <ul className="mt-4 space-y-2 text-sm">
              <li>✓ 5 uploads per month</li>
              <li>✓ 2 languages</li>
              <li>✓ 1 team member</li>
            </ul>
          </CardContent>
          <CardFooter>
            <Button disabled variant="outline" className="w-full">
              {currentPlan === "FREE" ? "Current Plan" : "Free Plan"}
            </Button>
          </CardFooter>
        </Card>

        <Card className={currentPlan === "STANDARD" ? "border-primary" : ""}>
          <CardHeader>
            <CardTitle>Standard</CardTitle>
            <CardDescription>For individuals and small teams.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              $10<span className="text-sm font-normal text-muted-foreground">/mo</span>
            </div>
            <ul className="mt-4 space-y-2 text-sm">
              <li>✓ 25 uploads per month</li>
              <li>✓ 5 languages</li>
              <li>✓ 5 team members</li>
            </ul>
          </CardContent>
          <CardFooter>
            <Button
              onClick={() => onUpgrade("STANDARD")}
              variant={currentPlan === "STANDARD" ? "outline" : "default"}
              className="w-full"
              disabled={currentPlan === "STANDARD" || isLoading}
            >
              {currentPlan === "STANDARD" ? "Current Plan" : "Upgrade to Standard"}
            </Button>
          </CardFooter>
        </Card>

        <Card className={currentPlan === "PRO" ? "border-primary" : ""}>
          <CardHeader>
            <CardTitle>Pro</CardTitle>
            <CardDescription>For power users and large teams.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              $30<span className="text-sm font-normal text-muted-foreground">/mo</span>
            </div>
            <ul className="mt-4 space-y-2 text-sm">
              <li>✓ Unlimited uploads</li>
              <li>✓ All languages</li>
              <li>✓ Unlimited members</li>
            </ul>
          </CardContent>
          <CardFooter>
            <Button
              onClick={() => onUpgrade("PRO")}
              variant={currentPlan === "PRO" ? "outline" : "default"}
              className="w-full"
              disabled={currentPlan === "PRO" || isLoading}
            >
              {currentPlan === "PRO" ? "Current Plan" : "Upgrade to Pro"}
            </Button>
          </CardFooter>
        </Card>
      </div>
    </section>
  );
}
