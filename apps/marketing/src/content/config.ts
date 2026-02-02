import { defineCollection, z } from 'astro:content';

const blog = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    description: z.string(),
    pubDate: z.coerce.date(),
    tags: z.array(z.string()).default([]),
    lang: z.enum(['en', 'de', 'es', 'fr', 'jp']).default('en'),
  }),
});

const docs = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    description: z.string(),
    order: z.number().optional(),
    lang: z.enum(['en', 'de', 'es', 'fr', 'jp']).default('en'),
  }),
});

const legal = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    lastUpdated: z.coerce.date(),
    lang: z.enum(['en', 'de', 'es', 'fr', 'jp']).default('en'),
  }),
});

export const collections = { blog, docs, legal };
