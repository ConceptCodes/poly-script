import { Button, Input, Label } from "@poly/ui";
import { useForm } from "@tanstack/react-form";
import { useAddPaymentMethod } from "../../../../hooks/useBilling";
import { addPaymentMethodSchema } from "../../schemas";

export function AddPaymentMethodForm() {
  const addPaymentMethod = useAddPaymentMethod();

  const form = useForm({
    defaultValues: {
      cardholderName: "",
    },
    onSubmit: async () => {
      addPaymentMethod.mutate({
        success_url: window.location.href,
        cancel_url: window.location.href,
      });
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
      >
        {(field) => (
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
      </form.Field>
      <Button type="submit" disabled={addPaymentMethod.isPending} className="w-full">
        {addPaymentMethod.isPending ? "Redirecting..." : "Add Payment Method"}
      </Button>
    </form>
  );
}
