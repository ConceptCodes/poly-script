import { useParams, useNavigate } from "react-router-dom";
import { Button } from "@poly/ui";
import { XCircle } from "lucide-react";

export function CheckoutCancelPage() {
  const { type } = useParams<{ type: string }>();
  const navigate = useNavigate();

  const getMessage = () => {
    if (type === "subscription") {
      return ({
        title: "Subscription Not Started",
        description:
          "The subscription upgrade was canceled. You can try again anytime.",
      });
    } else if (type === "credits") {
      return ({
        title: "Credits Purchase Canceled",
        description: "The credit purchase was canceled. You can try again anytime.",
      });
    }
    return ({
      title: "Payment Canceled",
      description: "The payment was canceled. You can try again anytime.",
    });
  };

  const { title, description } = getMessage();

  return (
    <div className="container mx-auto flex min-h-[60vh] items-center justify-center p-6">
      <div className="flex max-w-md flex-col items-center space-y-6 text-center">
        <XCircle className="h-24 w-24 text-muted-foreground" />
        <h1 className="text-3xl font-bold">{title}</h1>
        <p className="text-muted-foreground">{description}</p>
        <div className="flex gap-4">
          <Button onClick={() => navigate("/billing")}>Return to Billing</Button>
          <Button variant="outline" onClick={() => navigate("/dashboard")}>
            Go to Dashboard
          </Button>
        </div>
      </div>
    </div>
  );
}
