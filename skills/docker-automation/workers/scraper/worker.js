#!/usr/bin/env node
/**
 * Scraper Worker - Web scraping genérico com Puppeteer
 * Output: JSON com conteúdo extraído
 */

const puppeteer = require('puppeteer-core');
const fs = require('fs');
const path = require('path');

// Config
const OUTPUT_DIR = process.env.SCRAPER_OUTPUT || '/data/scraper/output';
const TIMEOUT = parseInt(process.env.TIMEOUT) || 30000;

async function scrape(url, selector) {
  const browser = await puppeteer.launch({
    executablePath: '/usr/bin/chromium-browser',
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage',
      '--disable-gpu'
    ]
  });

  try {
    const page = await browser.newPage();
    await page.goto(url, { waitUntil: 'networkidle2', timeout: TIMEOUT });
    
    // Extrai conteúdo
    const content = await page.evaluate((sel) => {
      if (!sel || sel === 'body') {
        return document.body.innerText;
      }
      
      const element = document.querySelector(sel);
      return element ? element.innerText : null;
    }, selector);

    // Extrai metadata
    const metadata = await page.evaluate(() => ({
      title: document.title,
      url: window.location.href,
      timestamp: new Date().toISOString()
    }));

    return {
      success: true,
      url: metadata.url,
      title: metadata.title,
      selector: selector || 'body',
      content: content,
      timestamp: metadata.timestamp
    };
  } catch (error) {
    return {
      success: false,
      url: url,
      error: error.message,
      timestamp: new Date().toISOString()
    };
  } finally {
    await browser.close();
  }
}

async function main() {
  const args = process.argv.slice(2);
  
  if (args.length < 1) {
    console.error('Uso: node worker.js <URL> [selector]');
    process.exit(1);
  }

  const url = args[0];
  const selector = args[1] || 'body';

  console.log(`Scraping: ${url} (selector: ${selector || 'body'})`);

  const result = await scrape(url, selector);

  // Salva resultado
  const outputPath = path.join(OUTPUT_DIR, `scrape_${Date.now()}.json`);
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  fs.writeFileSync(outputPath, JSON.stringify(result, null, 2));

  console.log(`✅ Resultado salvo em: ${outputPath}`);
  console.log(JSON.stringify(result, null, 2));
}

main().catch(console.error);
