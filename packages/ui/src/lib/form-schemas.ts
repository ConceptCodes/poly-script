import { z } from 'zod';

// at least 8 characters
// at least one uppercase
// at least one lowercase
// at least one number
// at least one special character
const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;

export const loginSchema = z.object({
  email: z.email(),
  password: z.string().regex(passwordRegex),
});

export const signupSchema = z.object({
  email: z.email(),
  password: z.string().regex(passwordRegex),
  confirmPassword: z.string().regex(passwordRegex),
  acceptTerms: z.boolean().refine(val => val === true, "You must accept terms"),
}).refine(data => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"],
});

export const teamCreateSchema = z.object({
  name: z.string().min(2, "Team name must be at least 2 characters"),
  host_language: z.enum(["en", "de", "es", "fr", "jp"]),
});

export const inviteMemberSchema = z.object({
  email: z.email(),
  role: z.enum(["ADMIN", "MEMBER", "VIEWER"]),
});
