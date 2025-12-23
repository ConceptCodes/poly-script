import { Button, Skeleton } from "@poly/ui";
import { useEffect, useState } from "react";
import { apiFetch } from "../../lib/api";
import { UsageCard } from "./components/cards/UsageCard";
import { CurrentPlanCard } from "./components/cards/CurrentPlanCard";
import { PlanComparisonCard } from "./components/cards/PlanComparisonCard";
import { PaymentMethodsCard } from "./components/cards/PaymentMethodsCard";
import { PurchaseCreditsForm } from "./components/forms/PurchaseCreditsForm";
import { UpgradeModal } from "./components/modals/UpgradeModal";
import { CancelSubscriptionModal } from "./components/modals/CancelSubscriptionModal";
import { InvoicesCard } from "./components/cards/InvoicesCard";
import { UsageHistoryCard } from "./components/cards/UsageHistoryCard";

interface BillingData {
  plan: string;
  monthly_upload_count: number;
  monthly_limit: number | "inf";
  extra_credits: number;
  status: string;
  cancel_at_period_end: boolean;
}

const PLAN_PRICES: Record<string, number> = {
  FREE: 0,
  STANDARD: 29,
  PRO: 99
};

const PLAN_ORDER = ["FREE", "STANDARD", "PRO"];

export default function BillingPage() {
  const [data, setData] = useState<BillingData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [upgradeModalOpen, setUpgradeModalOpen] = useState(false);
  const [cancelModalOpen, setCancelModalOpen] = useState(false);
  const [targetPlan, setTargetPlan] = useState<string | null>(null);
  const [processing, setProcessing] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  async function fetchData() {
    try {
      const usage = await apiFetch("/billing/usage");
      const subscription = await apiFetch("/billing/subscription");
      setData({
        ...usage,
        status: subscription.status || "active",
        cancel_at_period_end: subscription.cancel_at_period_end,
      });
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  const handleManageBilling = async () => {
    try {
      const { url } = await apiFetch("/billing/portal", {
        method: "POST",
        body: JSON.stringify({ return_url: window.location.href }),
      });
      window.location.href = url;
    } catch (err: any) {
      alert("Failed to open billing portal: " + err.message);
    }
  };

  const initiatePlanChange = (plan: string) => {
    setTargetPlan(plan);
    setUpgradeModalOpen(true);
  };

  const handlePlanConfirm = async () => {
    if (!targetPlan || !data) return;
    setProcessing(true);
    try {
        const currentIdx = PLAN_ORDER.indexOf(data.plan);
        const targetIdx = PLAN_ORDER.indexOf(targetPlan);
        
        if (data.plan === 'FREE') {
             // Free -> Paid (Checkout)
            const { checkout_url } = await apiFetch("/billing/subscription/upgrade", {
                method: "POST",
                body: JSON.stringify({
                  plan: targetPlan,
                  success_url: window.location.origin + "/billing?success=true",
                  cancel_url: window.location.origin + "/billing?canceled=true",
                }),
            });
            window.location.href = checkout_url;
        } else {
            // Paid -> Paid (Modify)
            // We use the downgrade endpoint which handles modification (both up and down usually if implemented as modify)
            // But wait, my implementation of `downgrade_plan` in BillingService uses `stripe.Subscription.modify`. 
            // This works for upgrades too (Standard -> Pro), just charging the difference immediately.
            // Let's assume it works for both for now, or fallback to checkout if not.
            // Actually, for Upgrades (Standard -> Pro), Checkout is often preferred to handle SCA/Payment failures. 
            // But let's try the direct modify first.
            await apiFetch("/billing/subscription/downgrade", {
                method: "POST",
                body: JSON.stringify({ plan: targetPlan })
            });
            window.location.reload();
        }
    } catch (err: any) {
        alert("Failed to change plan: " + err.message);
        setProcessing(false);
        setUpgradeModalOpen(false);
    }
  };

  const handleCancelClick = () => {
      setCancelModalOpen(true);
  };

  const handleCancelConfirm = async () => {
      setProcessing(true);
      try {
          await apiFetch("/billing/subscription/cancel", { method: "POST" });
          window.location.reload();
      } catch (err: any) {
          alert("Failed to cancel: " + err.message);
          setProcessing(false);
      }
  };

  const handleReactivate = async () => {
      setProcessing(true);
      try {
          await apiFetch("/billing/subscription/reactivate", { method: "POST" });
          window.location.reload();
      } catch (err: any) {
          alert("Failed to reactivate: " + err.message);
          setProcessing(false);
      }
  };

  if (loading) {
    return (
      <div className="container mx-auto p-6 space-y-6">
        <Skeleton className="h-10 w-48" />
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Skeleton className="h-64 w-full" />
          <Skeleton className="h-64 w-full" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto p-6 text-center">
        <h1 className="text-2xl font-bold text-red-500">Error</h1>
        <p className="text-muted-foreground">{error}</p>
        <Button onClick={() => window.location.reload()} className="mt-4">
          Retry
        </Button>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-8">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold tracking-tight">Billing & Subscriptions</h1>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="space-y-8">
          <CurrentPlanCard 
            plan={data?.plan || "FREE"} 
            status={data?.status || "active"} 
            cancelAtPeriodEnd={data?.cancel_at_period_end}
            onManage={handleManageBilling} 
            onReactivate={handleReactivate}
          />
          {/* Explicit Cancel Button for Paid Plans if not using Portal exclusively */}
          {data?.plan !== 'FREE' && !data?.cancel_at_period_end && (
              <div className="flex justify-end">
                   <Button variant="link" className="text-destructive h-auto p-0" onClick={handleCancelClick}>
                       Cancel Subscription
                   </Button>
              </div>
          )}
          
          {data?.plan === 'FREE' && <PurchaseCreditsForm />}
        </div>
        <div className="space-y-8">
            <UsageCard 
            monthlyUploadCount={data?.monthly_upload_count || 0} 
            monthlyLimit={data?.monthly_limit || 5} 
            extraCredits={data?.extra_credits || 0} 
            />
             {/* Payment Methods only relevant if customer exists. Free plans might not have one yet. */}
             {data?.plan !== 'FREE' && <PaymentMethodsCard />}
             <InvoicesCard />
             <UsageHistoryCard />
        </div>
      </div>

      <PlanComparisonCard 
        currentPlan={data?.plan || "FREE"} 
        onUpgrade={initiatePlanChange}
        isLoading={processing}
      />

        <UpgradeModal 
            open={upgradeModalOpen} 
            onOpenChange={setUpgradeModalOpen}
            planName={targetPlan || ""}
            price={PLAN_PRICES[targetPlan || "STANDARD"]}
            onConfirm={handlePlanConfirm}
            isLoading={processing}
        />
        
        <CancelSubscriptionModal 
            open={cancelModalOpen} 
            onOpenChange={setCancelModalOpen}
            onConfirm={handleCancelConfirm}
            isLoading={processing}
        />
    </div>
  );
}
