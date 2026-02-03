import { Button, Skeleton, useToast } from "@poly/ui";
import { useState } from "react";
import {
  useCancelSubscription,
  useCreatePortalSession,
  useDowngradeSubscription,
  useReactivateSubscription,
  useSubscription,
  useUpgradeSubscription,
  useUsage,
} from "../../hooks/useBilling";
import { CurrentPlanCard } from "./components/cards/CurrentPlanCard";
import { InvoicesCard } from "./components/cards/InvoicesCard";
import { PaymentMethodsCard } from "./components/cards/PaymentMethodsCard";
import { PlanComparisonCard } from "./components/cards/PlanComparisonCard";
import { UsageCard } from "./components/cards/UsageCard";
import { UsageHistoryCard } from "./components/cards/UsageHistoryCard";
import { PurchaseCreditsForm } from "./components/forms/PurchaseCreditsForm";
import { CancelSubscriptionModal } from "./components/modals/CancelSubscriptionModal";
import { UpgradeModal } from "./components/modals/UpgradeModal";

const PLAN_PRICES: Record<string, number> = {
  FREE: 0,
  STANDARD: 10,
  PRO: 30,
};

export function BillingPage() {
  const [upgradeModalOpen, setUpgradeModalOpen] = useState(false);
  const [cancelModalOpen, setCancelModalOpen] = useState(false);
  const [targetPlan, setTargetPlan] = useState<string | null>(null);
  const { toast } = useToast();

  // Queries
  const { data: usage, isLoading: usageLoading, error: usageError } = useUsage();
  const { data: subscription, isLoading: subscriptionLoading } = useSubscription();

  // Mutations
  const createPortalSession = useCreatePortalSession();
  const upgradeSubscription = useUpgradeSubscription();
  const downgradeSubscription = useDowngradeSubscription();
  const cancelSubscription = useCancelSubscription();
  const reactivateSubscription = useReactivateSubscription();

  const loading = usageLoading || subscriptionLoading;
  const error = usageError?.message;
  const processing =
    upgradeSubscription.isPending ||
    downgradeSubscription.isPending ||
    cancelSubscription.isPending ||
    reactivateSubscription.isPending;

  // Combine usage and subscription data
  const data =
    usage && subscription
      ? {
          ...usage,
          status: subscription.status || "active",
          cancel_at_period_end: subscription.cancel_at_period_end,
          current_period_start: subscription.current_period_start,
          current_period_end: subscription.current_period_end,
        }
      : null;

  const handleManageBilling = () => {
    createPortalSession.mutate(undefined);
  };

  const initiatePlanChange = (plan: string) => {
    setTargetPlan(plan);
    setUpgradeModalOpen(true);
  };

  const handlePlanConfirm = () => {
    if (!targetPlan || !data) return;

    if (data.plan === "FREE") {
      // Free -> Paid (Checkout)
      upgradeSubscription.mutate({ plan: targetPlan });
    } else {
      // Paid -> Paid (Modify)
      downgradeSubscription.mutate(targetPlan, {
        onSuccess: () => {
          window.location.reload();
        },
        onError: (err: unknown) => {
          const message = err instanceof Error ? err.message : "Unable to change plan.";
          toast({
            title: "Plan change failed",
            description: message,
            variant: "destructive",
          });
          setUpgradeModalOpen(false);
        },
      });
    }
  };

  const handleCancelClick = () => {
    setCancelModalOpen(true);
  };

  const handleCancelConfirm = () => {
    cancelSubscription.mutate(undefined, {
      onSuccess: () => {
        window.location.reload();
      },
      onError: (err: unknown) => {
        const message = err instanceof Error ? err.message : "Unable to cancel subscription.";
        toast({
          title: "Cancellation failed",
          description: message,
          variant: "destructive",
        });
      },
    });
  };

  const handleReactivate = () => {
    reactivateSubscription.mutate(undefined, {
      onSuccess: () => {
        window.location.reload();
      },
      onError: (err: unknown) => {
        const message = err instanceof Error ? err.message : "Unable to reactivate subscription.";
        toast({
          title: "Reactivation failed",
          description: message,
          variant: "destructive",
        });
      },
    });
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
            currentPeriodStart={data?.current_period_start}
            currentPeriodEnd={data?.current_period_end}
            planPrice={PLAN_PRICES[data?.plan || "FREE"]}
            onManage={handleManageBilling}
            onReactivate={handleReactivate}
          />
          {/* Explicit Cancel Button for Paid Plans if not using Portal exclusively */}
          {data?.plan !== "FREE" && !data?.cancel_at_period_end && (
            <div className="flex justify-end">
              <Button
                variant="link"
                className="text-destructive h-auto p-0"
                onClick={handleCancelClick}
              >
                Cancel Subscription
              </Button>
            </div>
          )}

          {data?.plan === "FREE" && <PurchaseCreditsForm />}
        </div>
        <div className="space-y-8">
          <UsageCard
            monthlyUploadCount={data?.monthly_upload_count || 0}
            monthlyLimit={data?.monthly_limit || 5}
            extraCredits={data?.extra_credits || 0}
          />
          {/* Payment Methods only relevant if customer exists. Free plans might not have one yet. */}
          {data?.plan !== "FREE" && <PaymentMethodsCard />}
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
