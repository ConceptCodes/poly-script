import { Button } from "@poly/ui";
import { CheckCircle2 } from "lucide-react";
import { useNavigate, useParams } from "react-router-dom";

export function CheckoutSuccessPage() {
  const { type } = useParams<{ type: string }>();
  const navigate = useNavigate();

  const getMessage = () => {
    if (type === "subscription") {
      return {
        title: "Subscription Activated!",
        description:
          "Your subscription has been successfully activated. You can now enjoy all the benefits of your new plan.",
      };
    } else if (type === "credits") {
      return {
        title: "Credits Purchased!",
        description: "Your credits have been added to your account and are ready to use.",
      };
    }
    return {
      title: "Payment Successful!",
      description: "Your payment has been processed successfully.",
    };
  };

  const { title, description } = getMessage();

  return (
    <div className="container mx-auto flex min-h-[60vh] items-center justify-center p-6">
      <div className="flex max-w-md flex-col items-center space-y-6 text-center">
        <CheckCircle2 className="h-24 w-24 text-success" />
        <h1 className="text-3xl font-bold">{title}</h1>
        <p className="text-muted-foreground">{description}</p>
        <div className="flex gap-4">
          <Button onClick={() => navigate("/billing")}>Go to Billing</Button>
          <Button variant="outline" onClick={() => navigate("/dashboard")}>
            Go to Dashboard
          </Button>
        </div>
      </div>
    </div>
  );
}
