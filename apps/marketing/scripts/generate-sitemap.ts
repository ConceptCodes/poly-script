import type { APIRoute } from 'astro';
import { getCollection } from 'astro:content';
import { locales } from '../src/lib/i18n';

export async function GET() {
  const pages = [];
  
  const staticPaths = ['', '/features', '/pricing', '/docs', '/blog', '/legal', '/contact'];
  
  for (const lang of locales) {
    for (const path of staticPaths) {
      pages.push({
        url: `https://polyscript.io/${lang}${path}`,
        lastmod: new Date().toISOString(),
        changefreq: 'weekly',
        priority: path === '' ? 1.0 : 0.8
      });
    }
  }
  
  const blogPosts = await getCollection('blog');
  for (const post of blogPosts) {
    pages.push({
      url: `https://polyscript.io/${post.data.lang}/blog/${post.slug}`,
      lastmod: post.data.pubDate.toISOString(),
      changefreq: 'monthly',
      priority: 0.6
    });
  }
  
  const docs = await getCollection('docs');
  for (const doc of docs) {
    pages.push({
      url: `https://polyscript.io/${doc.data.lang}/docs/${doc.slug}`,
      lastmod: new Date().toISOString(),
      changefreq: 'monthly',
      priority: 0.7
    });
  }
  
  const legal = await getCollection('legal');
  for (const doc of legal) {
    pages.push({
      url: `https://polyscript.io/${doc.data.lang}/legal/${doc.slug}`,
      lastmod: doc.data.lastUpdated.toISOString(),
      changefreq: 'monthly',
      priority: 0.5
    });
  }
  
  const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${pages.map(page => `  <url>
    <loc>${page.url}</loc>
    <lastmod>${page.lastmod}</lastmod>
    <changefreq>${page.changefreq}</changefreq>
    <priority>${page.priority}</priority>
  </url>`).join('\n')}
</urlset>`;
  
  return new Response(sitemap, {
    headers: {
      'Content-Type': 'application/xml',
      'Cache-Control': 'public, max-age=3600'
    }
  });
}
