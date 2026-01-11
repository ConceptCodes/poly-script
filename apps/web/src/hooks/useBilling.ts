import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "../lib/api";
import type {
  UsageResponse,
  SubscriptionResponse,
  CheckoutResponse,
  PortalResponse,
  PricingData,
} from "../types/api";

// Query Keys
export const billingKeys = {
  all: ["billing"] as const,
  usage: () => [...billingKeys.all, "usage"] as const,
  subscription: () => [...billingKeys.all, "subscription"] as const,
  pricing: () => [...billingKeys.all, "pricing"] as const,
  invoices: () => [...billingKeys.all, "invoices"] as const,
  paymentMethods: () => [...billingKeys.all, "payment-methods"] as const,
  usageHistory: () => [...billingKeys.all, "usage-history"] as const,
};

// Queries
export function useUsage() {
  return useQuery({
    queryKey: billingKeys.usage(),
    queryFn: () => apiFetch<UsageResponse>("/billing/usage"),
  });
}

export function useSubscription() {
  return useQuery({
    queryKey: billingKeys.subscription(),
    queryFn: () => apiFetch<SubscriptionResponse>("/billing/subscription"),
  });
}

export function usePricing() {
  return useQuery({
    queryKey: billingKeys.pricing(),
    queryFn: () => apiFetch<PricingData>("/billing/pricing"),
  });
}

export function useInvoices() {
  return useQuery({
    queryKey: billingKeys.invoices(),
    queryFn: () => apiFetch<any[]>("/billing/invoices"),
  });
}

export function usePaymentMethods() {
  return useQuery({
    queryKey: billingKeys.paymentMethods(),
    queryFn: () => apiFetch<any[]>("/billing/payment-methods"),
  });
}

export function useUsageHistory() {
  return useQuery({
    queryKey: billingKeys.usageHistory(),
    queryFn: () => apiFetch<any>("/billing/usage-history"),
  });
}

// Mutations
export function useCreatePortalSession() {
  return useMutation({
    mutationFn: (returnUrl?: string) =>
      apiFetch<PortalResponse>("/billing/portal", {
        method: "POST",
        body: { return_url: returnUrl || window.location.origin + "/billing" },
      }),
    onSuccess: (data) => {
      window.location.href = data.url;
    },
  });
}

export function useUpgradeSubscription() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (params: { plan: string }) =>
      apiFetch<CheckoutResponse>("/billing/subscription/upgrade", {
        method: "POST",
        body: {
          plan: params.plan,
          success_url: window.location.origin + "/checkout/success?type=subscription",
          cancel_url: window.location.origin + "/checkout/cancel?type=subscription",
        },
      }),
    onSuccess: (data) => {
      window.location.href = data.checkout_url;
    },
  });
}

export function useDowngradeSubscription() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (plan: string) =>
      apiFetch("/billing/subscription/downgrade", {
        method: "POST",
        body: { plan },
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: billingKeys.subscription() });
      queryClient.invalidateQueries({ queryKey: billingKeys.usage() });
    },
  });
}

export function useCancelSubscription() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: () =>
      apiFetch("/billing/subscription/cancel", {
        method: "POST",
        body: { at_period_end: true },
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: billingKeys.subscription() });
    },
  });
}

export function useReactivateSubscription() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: () =>
      apiFetch("/billing/subscription/reactivate", {
        method: "POST",
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: billingKeys.subscription() });
    },
  });
}

export function usePurchaseCredits() {
  return useMutation({
    mutationFn: (params: { amount: number }) =>
      apiFetch<CheckoutResponse>("/billing/credits/purchase", {
        method: "POST",
        body: {
          amount: params.amount,
          success_url: window.location.origin + "/checkout/success?type=credits",
          cancel_url: window.location.origin + "/checkout/cancel?type=credits",
        },
      }),
    onSuccess: (data) => {
      window.location.href = data.checkout_url;
    },
  });
}

export function useAddPaymentMethod() {
  return useMutation({
    mutationFn: (params: { success_url: string; cancel_url: string }) =>
      apiFetch<CheckoutResponse>("/billing/payment-methods", {
        method: "POST",
        body: params,
      }),
    onSuccess: (data) => {
      window.location.href = data.checkout_url;
    },
  });
}

export function useDeletePaymentMethod() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (paymentMethodId: string) =>
      apiFetch(`/billing/payment-methods/${paymentMethodId}`, {
        method: "DELETE",
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: billingKeys.paymentMethods() });
    },
  });
}
