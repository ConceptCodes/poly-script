import { z } from 'zod';

export const uploadOptionsSchema = z.object({
  language: z.string().nullable(),
  engine: z.string().nullable(),
  timestamps: z.boolean().default(true),
  diarization: z.boolean().default(false),
});
