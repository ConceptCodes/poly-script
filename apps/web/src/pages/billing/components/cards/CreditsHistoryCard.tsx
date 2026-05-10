import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@poly/ui";
import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";

interface CreditPurchase {
  created_at: string;
  amount: number;
  price_paid: number;
  currency: string;
}

export function CreditsHistoryCard() {
  const [items, setItems] = useState<CreditPurchase[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadHistory = async () => {
      try {
        const data = await apiFetch<CreditPurchase[]>("/billing/credits/history");
        setItems(data || []);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    loadHistory();
  }, []);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Credit Purchase History</CardTitle>
        <CardDescription>Recent top-ups and one-time credit purchases.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        {loading ? (
          <p className="text-sm text-muted-foreground">Loading purchase history...</p>
        ) : items.length === 0 ? (
          <p className="text-sm text-muted-foreground">No credit purchases yet.</p>
        ) : (
          <div className="space-y-2">
            {items.slice(0, 10).map((item, idx) => (
              <div
                key={`${item.created_at}-${idx}`}
                className="flex items-center justify-between border rounded p-3"
              >
                <div>
                  <p className="text-sm font-medium">{item.amount} credits</p>
                  <p className="text-xs text-muted-foreground">
                    {item.currency.toUpperCase()} {(item.price_paid / 100).toFixed(2)}
                  </p>
                </div>
                <p className="text-xs text-muted-foreground">
                  {new Date(item.created_at).toLocaleDateString()}
                </p>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
