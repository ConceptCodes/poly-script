import { Button, Input, Label, useToast } from "@poly/ui";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useEffect, useRef, useState } from "react";
import { apiFetch } from "@/lib/api";
import { billingKeys } from "../../../../hooks/useBilling";
import { addPaymentMethodSchema } from "../../schemas";

declare global {
  interface Window {
    Stripe?: (publishableKey: string) => StripeInstance;
  }
}

interface StripeInstance {
  elements(): StripeElementsInstance;
  confirmCardSetup(
    clientSecret: string,
    options: {
      payment_method: {
        card: StripeCardElement;
        billing_details?: { name?: string };
      };
    },
  ): Promise<{ error?: { message?: string } }>;
}

interface StripeElementsInstance {
  create(type: "card", options?: Record<string, unknown>): StripeCardElement;
}

interface StripeCardElement {
  mount(target: HTMLElement): void;
  unmount(): void;
}

async function loadStripeJs(): Promise<void> {
  if (typeof window === "undefined") return;
  if (window.Stripe) return;

  await new Promise<void>((resolve, reject) => {
    const existingScript = document.querySelector<HTMLScriptElement>(
      'script[data-stripe-js="true"]',
    );
    if (existingScript) {
      if (window.Stripe) {
        resolve();
        return;
      }
      existingScript.addEventListener("load", () => resolve(), { once: true });
      existingScript.addEventListener("error", () => reject(new Error("Failed to load Stripe")), {
        once: true,
      });
      return;
    }

    const script = document.createElement("script");
    script.src = "https://js.stripe.com/v3/";
    script.async = true;
    script.dataset.stripeJs = "true";
    script.onload = () => resolve();
    script.onerror = () => reject(new Error("Failed to load Stripe"));
    document.head.appendChild(script);
  });
}

export function AddPaymentMethodForm() {
  const queryClient = useQueryClient();
  const { toast } = useToast();
  const [cardholderName, setCardholderName] = useState("");
  const [loadingStripe, setLoadingStripe] = useState(true);
  const [submitError, setSubmitError] = useState("");
  const [cardReady, setCardReady] = useState(false);
  const mountRef = useRef<HTMLDivElement | null>(null);
  const stripeRef = useRef<StripeInstance | null>(null);
  const cardRef = useRef<StripeCardElement | null>(null);

  const setupIntentMutation = useMutation({
    mutationFn: async () => {
      if (!stripeRef.current || !cardRef.current) {
        throw new Error("Stripe is not ready");
      }

      const { client_secret } = await apiFetch<{ client_secret: string }>(
        "/billing/payment-methods/setup-intent",
        {
          method: "POST",
        },
      );

      const result = await stripeRef.current.confirmCardSetup(client_secret, {
        payment_method: {
          card: cardRef.current,
          billing_details: {
            name: cardholderName.trim() || undefined,
          },
        },
      });

      if (result.error) {
        throw new Error(result.error.message || "Failed to add payment method");
      }

      await queryClient.invalidateQueries({ queryKey: billingKeys.paymentMethods() });
    },
    onSuccess: () => {
      setCardholderName("");
      setSubmitError("");
      toast({
        title: "Payment method added",
        description: "Your new card is ready for billing.",
      });
    },
    onError: (error: unknown) => {
      setSubmitError(error instanceof Error ? error.message : "Failed to add payment method");
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to add payment method",
        variant: "destructive",
      });
    },
  });

  useEffect(() => {
    let cancelled = false;

    const initializeStripe = async () => {
      try {
        const publishableKey = import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY;
        if (!publishableKey) {
          throw new Error("Stripe publishable key is not configured");
        }

        await loadStripeJs();
        if (cancelled || !mountRef.current || !window.Stripe) {
          return;
        }

        const stripe = window.Stripe(publishableKey);
        const elements = stripe.elements();
        const cardElement = elements.create("card", {
          hidePostalCode: true,
        });

        cardElement.mount(mountRef.current);
        stripeRef.current = stripe;
        cardRef.current = cardElement;
        setCardReady(true);
      } catch (error) {
        setSubmitError(error instanceof Error ? error.message : "Failed to load Stripe");
      } finally {
        setLoadingStripe(false);
      }
    };

    void initializeStripe();

    return () => {
      cancelled = true;
      cardRef.current?.unmount();
      cardRef.current = null;
      stripeRef.current = null;
    };
  }, []);

  return (
    <div className="space-y-3">
      <div className="space-y-2">
        <Label htmlFor="cardholderName">Cardholder Name</Label>
        <Input
          id="cardholderName"
          value={cardholderName}
          onChange={(e) => setCardholderName(e.target.value)}
          placeholder="Jane Doe"
        />
      </div>

      <div className="space-y-2">
        <Label>Card details</Label>
        <div ref={mountRef} className="rounded-md border bg-background p-3" />
        {!cardReady && loadingStripe && (
          <p className="text-xs text-muted-foreground">Loading secure card entry...</p>
        )}
      </div>

      {submitError && <p className="text-sm text-destructive">{submitError}</p>}

      <Button
        type="button"
        disabled={setupIntentMutation.isPending || loadingStripe || !cardReady}
        onClick={() => {
          setSubmitError("");
          if (!addPaymentMethodSchema.shape.cardholderName.safeParse(cardholderName).success) {
            setSubmitError("Cardholder name is required");
            return;
          }
          setupIntentMutation.mutate();
        }}
        className="w-full"
      >
        {setupIntentMutation.isPending ? "Saving..." : "Add Card"}
      </Button>
    </div>
  );
}
