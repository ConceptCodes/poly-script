import { useForm } from "@tanstack/react-form";
import {
  Button,
  Input,
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  Label,
} from "@poly/ui";
import { apiFetch } from "../../../../lib/api";
import { useState } from "react";
import { purchaseCreditsSchema } from "../../schemas";
import { ConfirmPurchaseModal } from "../modals/ConfirmPurchaseModal";

export function PurchaseCreditsForm() {
  const [loading, setLoading] = useState(false);
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [pendingAmount, setPendingAmount] = useState(10);

  const form = useForm({
    defaultValues: {
      amount: 10,
    },
    onSubmit: async ({ value }) => {
      setPendingAmount(value.amount);
      setConfirmOpen(true);
    },
  });

  const handleConfirm = async () => {
    setLoading(true);
    try {
      const { checkout_url } = await apiFetch("/billing/credits/purchase", {
        method: "POST",
        body: JSON.stringify({
          amount: pendingAmount,
          success_url: window.location.origin + "/billing?success=true",
          cancel_url: window.location.origin + "/billing?canceled=true",
        }),
      });
      window.location.href = checkout_url;
    } catch (err: any) {
      alert("Failed to start checkout: " + err.message);
      setLoading(false);
      setConfirmOpen(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Purchase Credits</CardTitle>
        <CardDescription>
          Buy extra credits to upload more files beyond your plan limit. $0.10 per credit.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            e.stopPropagation();
            form.handleSubmit();
          }}
          className="space-y-4"
        >
          <form.Field
            name="amount"
            validators={{
              onChange: ({ value }) => {
                const result = purchaseCreditsSchema.shape.amount.safeParse(value);
                return result.success ? undefined : result.error.issues[0].message;
              },
            }}
            children={(field) => (
              <div className="space-y-2">
                <Label htmlFor={field.name}>Amount</Label>
                <div className="flex space-x-2">
                  <Input
                    id={field.name}
                    type="number"
                    value={field.state.value}
                    onBlur={field.handleBlur}
                    onChange={(e) => field.handleChange(e.target.valueAsNumber)}
                  />
                  <div className="flex items-center text-sm text-muted-foreground whitespace-nowrap">
                    = ${(field.state.value * 0.1).toFixed(2)}
                  </div>
                </div>
                {field.state.meta.errors ? (
                  <p className="text-sm text-destructive">{field.state.meta.errors.join(", ")}</p>
                ) : null}
              </div>
            )}
          />
          <Button type="submit" disabled={loading} className="w-full">
            {loading ? "Processing..." : "Buy Credits"}
          </Button>
        </form>
      </CardContent>
      <ConfirmPurchaseModal
        open={confirmOpen}
        onOpenChange={setConfirmOpen}
        credits={pendingAmount}
        totalPrice={(pendingAmount * 0.1).toFixed(2)}
        onConfirm={handleConfirm}
        isLoading={loading}
      />
    </Card>
  );
}
