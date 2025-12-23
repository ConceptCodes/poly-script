import { useForm } from '@tanstack/react-form';
import { z } from 'zod';
import { Button, Input, Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter, Label } from '@poly/ui';
import { apiFetch } from '../../../../lib/api';
import { useState } from 'react';

const purchaseCreditsSchema = z.object({
  amount: z.number().min(10, "Minimum 10 credits").max(1000, "Maximum 1000 credits"),
});

export function PurchaseCreditsForm() {
  const [loading, setLoading] = useState(false);

  const form = useForm({
    defaultValues: {
      amount: 10,
    },
    onSubmit: async ({ value }) => {
      setLoading(true);
      try {
        const { checkout_url } = await apiFetch("/billing/credits/purchase", {
          method: "POST",
          body: JSON.stringify({
            amount: value.amount,
            success_url: window.location.origin + "/billing?success=true",
            cancel_url: window.location.origin + "/billing?canceled=true",
          }),
        });
        window.location.href = checkout_url;
      } catch (err: any) {
        alert("Failed to start checkout: " + err.message);
        setLoading(false);
      }
    },
  });

  return (
    <Card>
      <CardHeader>
        <CardTitle>Purchase Credits</CardTitle>
        <CardDescription>
          Buy extra credits to upload more files beyond your plan limit.
          $0.10 per credit.
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
                    = ${(field.state.value * 0.10).toFixed(2)}
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
    </Card>
  );
}
