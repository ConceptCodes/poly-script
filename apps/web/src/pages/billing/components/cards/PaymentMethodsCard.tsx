import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
  CardFooter,
  Button,
} from "@poly/ui";
import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";
import { Loader2, Trash2 } from "lucide-react";
import { AddPaymentMethodForm } from "../forms/AddPaymentMethodForm";

interface PaymentMethod {
  id: string;
  brand: string;
  last4: string;
  exp_month: number;
  exp_year: number;
}

export function PaymentMethodsCard() {
  const [methods, setMethods] = useState<PaymentMethod[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadMethods();
  }, []);

  const loadMethods = async () => {
    try {
      const data = await apiFetch<PaymentMethod[]>("/billing/payment-methods");
      setMethods(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Are you sure you want to remove this payment method?")) return;
    try {
      await apiFetch(`/billing/payment-methods/${id}`, { method: "DELETE" });
      await loadMethods();
    } catch (err) {
      alert("Failed to delete payment method");
    }
  };

  const handleSetDefault = async (id: string) => {
    try {
      await apiFetch(`/billing/payment-methods/${id}/default`, { method: "PATCH" });
      await loadMethods();
    } catch (err) {
      alert("Failed to set default payment method");
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Payment Methods</CardTitle>
        <CardDescription>Manage your credit cards.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {loading ? (
          <div className="flex justify-center p-4">
            <Loader2 className="animate-spin" />
          </div>
        ) : methods.length === 0 ? (
          <p className="text-muted-foreground text-sm">No payment methods attached.</p>
        ) : (
          <div className="space-y-2">
            {methods.map((pm) => (
              <div key={pm.id} className="flex justify-between items-center border p-3 rounded">
                <div className="flex items-center gap-2">
                  {/* Simply text for brand/last4 for now, could use icons */}
                  <div className="flex flex-col">
                    <span className="capitalize font-medium text-sm">
                      {pm.brand} •••• {pm.last4}
                    </span>
                    <span className="text-xs text-muted-foreground">
                      Exp {pm.exp_month}/{pm.exp_year}
                    </span>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Button variant="outline" size="sm" onClick={() => handleSetDefault(pm.id)}>
                    Set Default
                  </Button>
                  <Button variant="ghost" size="icon" onClick={() => handleDelete(pm.id)}>
                    <Trash2 className="h-4 w-4 text-red-500" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
      <CardFooter>
        <div className="w-full space-y-3">
          <AddPaymentMethodForm />
          <p className="text-xs text-muted-foreground">
            You'll be redirected to Stripe to securely add a card.
          </p>
        </div>
      </CardFooter>
    </Card>
  );
}
