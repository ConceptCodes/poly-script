import { z } from "zod";

const CREDIT_BUNDLES = [10, 50, 100] as const;

export const purchaseCreditsSchema = z.object({
  amount: z
    .number()
    .refine(
      (val) => CREDIT_BUNDLES.includes(val as (typeof CREDIT_BUNDLES)[number]),
      "Must be 10, 50, or 100 credits",
    ),
});

export const addPaymentMethodSchema = z.object({
  cardholderName: z.string().min(1, "Cardholder name is required"),
});
