import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@poly/ui";
import { useEffect, useState } from "react";
import { apiFetch } from "../../../../lib/api";

interface UsageItem {
  action: string;
  amount: number;
  description?: string | null;
  created_at: string;
}

export function UsageHistoryCard() {
  const [items, setItems] = useState<UsageItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadHistory = async () => {
      try {
        const data = await apiFetch("/billing/usage/history");
        setItems(data.items || []);
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
        <CardTitle>Usage History</CardTitle>
        <CardDescription>Recent usage activity.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        {loading ? (
          <p className="text-sm text-muted-foreground">Loading usage history...</p>
        ) : items.length === 0 ? (
          <p className="text-sm text-muted-foreground">No usage history yet.</p>
        ) : (
          <div className="space-y-2">
            {items.slice(0, 10).map((item, idx) => (
              <div
                key={`${item.created_at}-${idx}`}
                className="flex items-center justify-between border rounded p-3"
              >
                <div>
                  <p className="text-sm font-medium capitalize">{item.action}</p>
                  <p className="text-xs text-muted-foreground">
                    {item.description || "Usage event"}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-medium">{item.amount}</p>
                  <p className="text-xs text-muted-foreground">
                    {new Date(item.created_at).toLocaleDateString()}
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
