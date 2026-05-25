#!/usr/bin/env python3
"""
Newsletter Worker - Coleta notícias de feeds RSS/Atom
Output: Markdown formatado no padrão Hermes newsletter
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

import feedparser
import requests
from dateutil import parser as date_parser

# Config
OUTPUT_DIR = os.getenv('NEWSLETTER_OUTPUT', '/data/newsletter/output')
FEEDS_FILE = os.getenv('NEWSLETTER_FEEDS', '/data/newsletter/feeds.json')
SEEN_FILE = os.getenv('NEWSLETTER_SEEN', '/data/newsletter/seen.json')

# Feeds padrão se não existir config
DEFAULT_FEEDS = [
    {"name": "TechCrunch", "url": "https://techcrunch.com/feed/"},
    {"name": "The Verge", "url": "https://www.theverge.com/rss/index.xml"},
    {"name": "Ars Technica", "url": "https://feeds.arstechnica.com/arstechnica/index"},
]

def load_seen():
    """Carrega IDs de notícias já vistas (últimas 24h)"""
    seen_path = Path(SEEN_FILE)
    if seen_path.exists():
        with open(seen_path) as f:
            data = json.load(f)
        # Limpa IDs com mais de 24h
        cutoff = datetime.now().timestamp() - 86400
        return {k: v for k, v in data.items() if v > cutoff}
    return {}

def save_seen(seen):
    """Salva IDs de notícias vistas"""
    seen_path = Path(SEEN_FILE)
    seen_path.parent.mkdir(parents=True, exist_ok=True)
    with open(seen_path, 'w') as f:
        json.dump(seen, f, indent=2)

def fetch_feed(name, url, seen_ids):
    """Baixa e parsea um feed RSS/Atom"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        feed = feedparser.parse(response.content)
        
        items = []
        for entry in feed.entries[:10]:  # Max 10 por feed
            entry_id = entry.get('id', entry.get('link', ''))
            
            # Pula se já visto
            if entry_id in seen_ids:
                continue
            
            # Parse data
            published = entry.get('published', entry.get('updated', ''))
            try:
                ts = date_parser.parse(published).timestamp()
            except:
                ts = datetime.now().timestamp()
            
            items.append({
                'title': entry.get('title', 'Sem título'),
                'link': entry.get('link', '#'),
                'published': published,
                'timestamp': ts,
                'source': name,
                'id': entry_id
            })
        
        return items
    except Exception as e:
        print(f"Erro ao processar {name}: {e}", file=sys.stderr)
        return []

def format_newsletter(items, section="AI"):
    """Formata notícias no padrão Hermes newsletter"""
    if not items:
        return ""
    
    output = f"## {section}\n\n"
    
    # Ordena por data (mais recente primeiro)
    items.sort(key=lambda x: x['timestamp'], reverse=True)
    
    for i, item in enumerate(items[:5]):  # Max 5 items
        output += f"- {item['title']} - {item['source']} ({item['link']})\n"
        if i < len(items) - 1:
            output += "\n"
    
    return output

def main():
    # Carrega feeds
    feeds_path = Path(FEEDS_FILE)
    if feeds_path.exists():
        with open(feeds_path) as f:
            feeds = json.load(f)
    else:
        feeds = DEFAULT_FEEDS
    
    # Carrega seen IDs
    seen = load_seen()
    
    # Coleta notícias
    all_items = []
    for feed in feeds:
        items = fetch_feed(feed['name'], feed['url'], seen)
        all_items.extend(items)
        # Marca como visto
        for item in items:
            seen[item['id']] = item['timestamp']
    
    # Salva seen IDs
    save_seen(seen)
    
    # Formata output
    output = format_newsletter(all_items, "AI News")
    
    # Salva resultado
    output_path = Path(OUTPUT_DIR)
    output_path.mkdir(parents=True, exist_ok=True)
    
    date_str = datetime.now().strftime('%Y-%m-%d')
    output_file = output_path / f"{date_str}.md"
    
    with open(output_file, 'w') as f:
        f.write(output)
    
    print(f"✅ Newsletter salva em: {output_file}")
    print(output)

if __name__ == '__main__':
    main()
