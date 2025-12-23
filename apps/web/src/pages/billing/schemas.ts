import { z } from "zod";

export const purchaseCreditsSchema = z.object({
  amount: z.number().min(10, "Minimum 10 credits").max(1000, "Maximum 1000 credits"),
});

export const addPaymentMethodSchema = z.object({
  cardholderName: z.string().min(1, "Cardholder name is required"),
});
