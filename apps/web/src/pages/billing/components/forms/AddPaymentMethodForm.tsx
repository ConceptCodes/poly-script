import { useForm } from "@tanstack/react-form";
import { Button, Input, Label } from "@poly/ui";
import { apiFetch } from "../../../../lib/api";
import { useState } from "react";
import { addPaymentMethodSchema } from "../../schemas";

export function AddPaymentMethodForm() {
  const [loading, setLoading] = useState(false);

  const form = useForm({
    defaultValues: {
      cardholderName: "",
    },
    onSubmit: async () => {
      setLoading(true);
      try {
        const { checkout_url } = await apiFetch("/billing/payment-methods", {
          method: "POST",
          body: JSON.stringify({
            success_url: window.location.href,
            cancel_url: window.location.href,
          }),
        });
        window.location.href = checkout_url;
      } catch (err: any) {
        alert("Failed to start setup session: " + err.message);
        setLoading(false);
      }
    },
  });

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        e.stopPropagation();
        form.handleSubmit();
      }}
      className="space-y-3"
    >
      <form.Field
        name="cardholderName"
        validators={{
          onChange: ({ value }) => {
            const result = addPaymentMethodSchema.shape.cardholderName.safeParse(value);
            return result.success ? undefined : result.error.issues[0].message;
          },
        }}
        children={(field) => (
          <div className="space-y-2">
            <Label htmlFor={field.name}>Cardholder Name</Label>
            <Input
              id={field.name}
              value={field.state.value}
              onBlur={field.handleBlur}
              onChange={(e) => field.handleChange(e.target.value)}
              placeholder="Jane Doe"
            />
            {field.state.meta.errors ? (
              <p className="text-sm text-destructive">{field.state.meta.errors.join(", ")}</p>
            ) : null}
          </div>
        )}
      />
      <Button type="submit" disabled={loading} className="w-full">
        {loading ? "Redirecting..." : "Add Payment Method"}
      </Button>
    </form>
  );
}
