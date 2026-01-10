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
import { useState } from "react";
import { purchaseCreditsSchema } from "../../schemas";
import { ConfirmPurchaseModal } from "../modals/ConfirmPurchaseModal";
import { usePurchaseCredits } from "../../../../hooks/useBilling";

export function PurchaseCreditsForm() {
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [pendingAmount, setPendingAmount] = useState(10);

  const purchaseCredits = usePurchaseCredits();

  const form = useForm({
    defaultValues: {
      amount: 10,
    },
    onSubmit: async ({ value }) => {
      setPendingAmount(value.amount);
      setConfirmOpen(true);
    },
  });

  const handleConfirm = () => {
    purchaseCredits.mutate({
      amount: pendingAmount,
      success_url: window.location.origin + "/billing?success=true",
      cancel_url: window.location.origin + "/billing?canceled=true",
    });
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Purchase Credits</CardTitle>
        <CardDescription>
          Buy extra credits to upload more files beyond your plan limit. $1.00 per credit.
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
                    = ${(field.state.value * 1).toFixed(2)}
                  </div>
                </div>
                {field.state.meta.errors ? (
                  <p className="text-sm text-destructive">{field.state.meta.errors.join(", ")}</p>
                ) : null}
              </div>
            )}
          />
          <Button type="submit" disabled={purchaseCredits.isPending} className="w-full">
            {purchaseCredits.isPending ? "Processing..." : "Buy Credits"}
          </Button>
        </form>
      </CardContent>
      <ConfirmPurchaseModal
        open={confirmOpen}
        onOpenChange={setConfirmOpen}
        credits={pendingAmount}
        totalPrice={(pendingAmount * 1).toFixed(2)}
        onConfirm={handleConfirm}
        isLoading={purchaseCredits.isPending}
      />
    </Card>
  );
}
