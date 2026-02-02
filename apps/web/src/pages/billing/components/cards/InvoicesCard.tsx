import { Card, CardContent, CardHeader, CardTitle, CardDescription, Button } from "@poly/ui";
import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";

interface Invoice {
  id: string;
  stripe_invoice_id: string;
  amount_paid: number;
  status: string;
  created_at: string;
  hosted_invoice_url?: string | null;
  invoice_pdf?: string | null;
}

export function InvoicesCard() {
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadInvoices = async () => {
      try {
        const data = await apiFetch<Invoice[]>("/billing/invoices");
        setInvoices(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    loadInvoices();
  }, []);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Invoices</CardTitle>
        <CardDescription>Your recent invoices.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        {loading ? (
          <p className="text-sm text-muted-foreground">Loading invoices...</p>
        ) : invoices.length === 0 ? (
          <p className="text-sm text-muted-foreground">No invoices found.</p>
        ) : (
          <div className="space-y-2">
            {invoices.map((invoice) => (
              <div
                key={invoice.id}
                className="flex items-center justify-between border rounded p-3"
              >
                <div className="space-y-1">
                  <p className="text-sm font-medium">
                    {new Date(invoice.created_at).toLocaleDateString()}
                  </p>
                  <p className="text-xs text-muted-foreground">{invoice.status.toUpperCase()}</p>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-sm font-medium">
                    ${(invoice.amount_paid / 100).toFixed(2)}
                  </span>
                  {(invoice.invoice_pdf || invoice.hosted_invoice_url) && (
                    <Button variant="outline" size="sm" asChild>
                      <a
                        href={invoice.invoice_pdf || invoice.hosted_invoice_url || "#"}
                        target="_blank"
                        rel="noreferrer"
                      >
                        Download PDF
                      </a>
                    </Button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
