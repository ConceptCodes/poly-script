import { z } from 'zod';

export const LANGUAGE_OPTIONS = [
  { code: 'en', name: 'English' },
  { code: 'de', name: 'German' },
  { code: 'es', name: 'Spanish' },
  { code: 'fr', name: 'French' },
  { code: 'ja', name: 'Japanese' },
  { code: 'it', name: 'Italian' },
  { code: 'pt', name: 'Portuguese' },
  { code: 'ru', name: 'Russian' },
  { code: 'zh', name: 'Chinese' },
] as const;

export const uploadOptionsSchema = z.object({
  language: z.string().nullable(),
  engine: z.string().nullable(),
  timestamps: z.boolean().default(true),
  diarization: z.boolean().default(false),
  target_language: z.string().regex(/^[a-z]{2}(-[A-Z]{2})?$/).nullable(),
});

export type UploadFormValues = z.infer<typeof uploadOptionsSchema>;

export interface PlanLimits {
  maxUploads?: number;
  maxTranslations?: number;
  maxTargetLanguages?: number;
}

export interface UploadPageProps {
  planType?: string;
  languageLimit?: number;
  targetLanguageLimit?: number;
}
