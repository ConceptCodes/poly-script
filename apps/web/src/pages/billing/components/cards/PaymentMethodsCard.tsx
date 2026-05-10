import {
  Button,
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
  ConfirmDialog,
  useToast, // Use toast for feedback
} from "@poly/ui";
import { Loader2, Trash2 } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";
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
  const [methodToDelete, setMethodToDelete] = useState<string | null>(null);
  const { toast } = useToast();

  const loadMethods = useCallback(async () => {
    try {
      const data = await apiFetch<PaymentMethod[]>("/billing/payment-methods");
      setMethods(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadMethods();
  }, [loadMethods]);

  const confirmDelete = async () => {
    if (!methodToDelete) return;
    try {
      await apiFetch(`/billing/payment-methods/${methodToDelete}`, {
        method: "DELETE",
      });
      await loadMethods();
      toast({
        title: "Payment method removed",
        description: "The payment method has been successfully removed.",
      });
    } catch (_err) {
      toast({
        title: "Error",
        description: "Failed to delete payment method",
        variant: "destructive",
      });
    } finally {
      setMethodToDelete(null);
    }
  };

  const handleSetDefault = async (id: string) => {
    try {
      await apiFetch(`/billing/payment-methods/${id}/default`, {
        method: "PATCH",
      });
      await loadMethods();
      toast({
        title: "Default updated",
        description: "Your default payment method has been updated.",
      });
    } catch (_err) {
      toast({
        title: "Error",
        description: "Failed to set default payment method",
        variant: "destructive",
      });
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Payment Methods</CardTitle>
        <CardDescription>Manage your credit cards directly in the app.</CardDescription>
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
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => setMethodToDelete(pm.id)}
                    aria-label="Delete payment method"
                  >
                    <Trash2 className="h-4 w-4 text-destructive" />
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
            Card details are collected with Stripe Elements and never touch our servers.
          </p>
        </div>
      </CardFooter>

      <ConfirmDialog
        open={!!methodToDelete}
        onOpenChange={(open) => !open && setMethodToDelete(null)}
        title="Remove Payment Method"
        description="Are you sure you want to remove this payment method?"
        onConfirm={confirmDelete}
        confirmText="Remove"
        variant="destructive"
      />
    </Card>
  );
}
