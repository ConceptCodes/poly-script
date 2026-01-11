import { useForm } from "@tanstack/react-form";
import {
  Button,
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  RadioGroup,
  RadioGroupItem,
  Label,
} from "@poly/ui";
import { useState } from "react";
import { ConfirmPurchaseModal } from "../modals/ConfirmPurchaseModal";
import { usePurchaseCredits } from "../../../../hooks/useBilling";

const CREDIT_BUNDLES = [
  { value: 10, label: "10 Credits", price: 10 },
  { value: 50, label: "50 Credits", price: 50 },
  { value: 100, label: "100 Credits", price: 100 },
];

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
    purchaseCredits.mutate({ amount: pendingAmount });
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Purchase Credits</CardTitle>
        <CardDescription>
          Buy extra credits to upload more files beyond your plan limit. $1.00 per
          credit.
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
            children={(field) => (
              <div className="space-y-4">
                <Label>Credit Package</Label>
                <RadioGroup
                  value={String(field.state.value)}
                  onValueChange={(value) =>
                    field.handleChange(parseInt(value, 10))
                  }
                >
                  {CREDIT_BUNDLES.map((bundle) => (
                    <div
                      key={bundle.value}
                      className="flex items-center space-x-3 rounded-md border p-4"
                    >
                      <RadioGroupItem
                        value={String(bundle.value)}
                        id={`bundle-${bundle.value}`}
                      />
                      <Label
                        htmlFor={`bundle-${bundle.value}`}
                        className="flex-1 cursor-pointer"
                      >
                        <div className="font-medium">{bundle.label}</div>
                        <div className="text-sm text-muted-foreground">
                          ${bundle.price.toFixed(2)}
                        </div>
                      </Label>
                    </div>
                  ))}
                </RadioGroup>
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
