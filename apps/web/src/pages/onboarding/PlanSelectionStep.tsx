import { Badge, Card, CardContent, Label } from "@poly/ui";
import { Info } from "lucide-react";
import { useTranslation } from "react-i18next";

type PlanSelectionStepProps = {
  data: {
    plan?: string;
    [key: string]: unknown;
  };
  updateData: (key: string, value: string) => void;
  onNext: () => void;
};

const plans = [
  {
    id: "FREE",
    name: "Free",
    price: "$0",
    features: ["5 uploads/month", "2 team members", "Basic support"],
  },
  {
    id: "STANDARD",
    name: "Standard",
    price: "$29",
    features: ["100 uploads/month", "10 team members", "Priority support"],
  },
  {
    id: "PRO",
    name: "Pro",
    price: "$99",
    features: ["Unlimited uploads", "25 team members", "24/7 support"],
  },
];

export function PlanSelectionStep({ data, updateData, onNext: _onNext }: PlanSelectionStepProps) {
  const { t } = useTranslation();

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2">
        <Info className="h-5 w-5 text-muted-foreground" />
        <h2 className="text-2xl font-bold">{t("onboarding.steps.plan")}</h2>
      </div>

      <div role="radiogroup" className="grid gap-4">
        {plans.map((plan) => (
          <Card
            key={plan.id}
            role="radio"
            aria-checked={data.plan === plan.id}
            tabIndex={0}
            className={`cursor-pointer transition-all hover:shadow-lg ${
              data.plan === plan.id ? "ring-2 ring-primary" : ""
            }`}
            onClick={() => updateData("plan", plan.id)}
          >
            <CardContent className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="space-y-2">
                  <Label className="text-xl font-semibold">{plan.name}</Label>
                  <div className="text-3xl font-bold text-primary">
                    {plan.price}
                    <span className="text-sm font-normal text-muted-foreground">/mo</span>
                  </div>
                </div>
                <div
                  className={`h-4 w-4 rounded-full border ${
                    data.plan === plan.id ? "border-primary bg-primary" : "border-muted-foreground"
                  }`}
                />
              </div>

              <ul className="space-y-2">
                {plan.features.map((feature) => (
                  <li key={feature} className="flex items-start gap-2">
                    <Badge variant="secondary" className="mt-0.5">
                      <div className="h-1.5 w-1.5 rounded-full bg-primary" />
                    </Badge>
                    <span className="text-sm text-muted-foreground">{feature}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
