import { z } from "zod";
import type { TFunction } from "i18next";

export const createLoginSchema = (t: TFunction) =>
  z.object({
    email: z.string().min(1, t("common.required")).email(t("auth.login.error")),
    password: z.string().min(1, t("common.required")),
  });

export const createSignupSchema = (t: TFunction) =>
  z
    .object({
      email: z.string().min(1, t("common.required")).email(t("auth.signup.error")),
      password: z.string().min(8, t("common.required")),
      confirmPassword: z.string().min(1, t("common.required")),
      terms: z.boolean().refine((val) => val === true, t("auth.signup.termsRequired")),
    })
    .refine((data) => data.password === data.confirmPassword, {
      message: t("auth.signup.passwordMismatch"),
      path: ["confirmPassword"],
    });

export const createForgotPasswordSchema = (t: TFunction) =>
  z.object({
    email: z.string().min(1, t("common.required")).email(t("auth.forgotPassword.error")),
  });

export const createResetPasswordSchema = (t: TFunction) =>
  z
    .object({
      password: z.string().min(8, t("common.required")),
      confirmPassword: z.string().min(1, t("common.required")),
    })
    .refine((data) => data.password === data.confirmPassword, {
      message: t("auth.signup.passwordMismatch"),
      path: ["confirmPassword"],
    });
