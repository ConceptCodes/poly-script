import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter, Button } from "@poly/ui";
import { useEffect, useState } from "react";
import { apiFetch } from "../../../../lib/api";
import { Loader2, Plus, Trash2 } from "lucide-react";

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
  const [adding, setAdding] = useState(false);

  useEffect(() => {
    loadMethods();
  }, []);

  const loadMethods = async () => {
    try {
      const data = await apiFetch("/billing/payment-methods");
      setMethods(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleAdd = async () => {
    setAdding(true);
    try {
      // In a real app we might want to check if success URL needs params
      const { checkout_url } = await apiFetch("/billing/payment-methods", {
        method: "POST",
        body: JSON.stringify({
           success_url: window.location.href, 
           cancel_url: window.location.href
        })
      });
      window.location.href = checkout_url;
    } catch (err) {
        alert("Failed to start setup session");
        setAdding(false);
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

  return (
    <Card>
      <CardHeader>
        <CardTitle>Payment Methods</CardTitle>
        <CardDescription>Manage your credit cards.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {loading ? (
             <div className="flex justify-center p-4"><Loader2 className="animate-spin" /></div>
        ) : methods.length === 0 ? (
            <p className="text-muted-foreground text-sm">No payment methods attached.</p>
        ) : (
            <div className="space-y-2">
                {methods.map(pm => (
                    <div key={pm.id} className="flex justify-between items-center border p-3 rounded">
                        <div className="flex items-center gap-2">
                             {/* Simply text for brand/last4 for now, could use icons */}
                            <div className="flex flex-col">
                                <span className="capitalize font-medium text-sm">{pm.brand} •••• {pm.last4}</span>
                                <span className="text-xs text-muted-foreground">Exp {pm.exp_month}/{pm.exp_year}</span>
                            </div>
                        </div>
                        <Button variant="ghost" size="icon" onClick={() => handleDelete(pm.id)}>
                            <Trash2 className="h-4 w-4 text-red-500" />
                        </Button>
                    </div>
                ))}
            </div>
        )}
      </CardContent>
      <CardFooter>
        <Button onClick={handleAdd} disabled={adding} variant="outline" className="w-full">
            {adding ? <Loader2 className="mr-2 h-4 w-4 animate-spin"/> : <Plus className="mr-2 h-4 w-4"/>}
            Add Payment Method
        </Button>
      </CardFooter>
    </Card>
  );
}
