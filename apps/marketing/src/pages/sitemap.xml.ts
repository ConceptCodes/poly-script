import type { APIRoute } from 'astro';
import { locales } from '../lib/i18n';

export async function GET() {
  const pages = [];
  
  const staticPaths = ['', '/features', '/pricing', '/docs', '/blog', '/legal', '/contact'];
  
  for (const lang of locales) {
    for (const path of staticPaths) {
      pages.push({
        url: 'https://polyscript.io/' + lang + path,
        lastmod: new Date().toISOString(),
        changefreq: 'weekly',
        priority: path === '' ? 1.0 : 0.8
      });
    }
  }
  
  let xml = '<?xml version="1.0" encoding="UTF-8"?>\n';
  xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n';
  
  for (const page of pages) {
    xml += '  <url>\n';
    xml += '    <loc>' + page.url + '</loc>\n';
    xml += '    <lastmod>' + page.lastmod + '</lastmod>\n';
    xml += '    <changefreq>' + page.changefreq + '</changefreq>\n';
    xml += '    <priority>' + page.priority + '</priority>\n';
    xml += '  </url>\n';
  }
  
  xml += '</urlset>';
  
  return new Response(xml, {
    headers: {
      'Content-Type': 'application/xml',
      'Cache-Control': 'public, max-age=3600'
    }
  });
}
