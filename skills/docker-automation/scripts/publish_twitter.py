#!/usr/bin/env python3
"""
Publish Newsletter to Twitter/X via xurl CLI
Estratégia 1: Thread (Fio) Resumo
"""

import sys
import os
import re
import json
import subprocess
from pathlib import Path
from datetime import datetime

# Path to xurl binary installed on the VM
XURL_PATH = "/home/ubuntu/.local/bin/xurl"

def calculate_x_length(text):
    """
    X API treats any URL as exactly 23 characters for length limits.
    """
    urls = re.findall(r'https?://[^\s\n)]+', text)
    length = len(text)
    for url in urls:
        length = length - len(url) + 23
    return length

def run_command(args):
    """Executes a CLI command and returns exit code, stdout, stderr"""
    try:
        result = subprocess.run(args, capture_output=True, text=True, check=False)
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return -1, "", str(e)

def check_xurl_auth():
    """Checks if xurl is installed and authenticated"""
    if not Path(XURL_PATH).exists():
        print(f"❌ Erro: Binário xurl não encontrado em {XURL_PATH}", file=sys.stderr)
        return False
        
    code, stdout, stderr = run_command([XURL_PATH, "auth", "status"])
    if code != 0:
        print(f"❌ Erro ao verificar autenticação do xurl: {stderr}", file=sys.stderr)
        return False
        
    if "No apps registered" in stdout or "No registered apps" in stdout or "oauth2: (none)" in stdout:
        print("⚠️ xurl instalado, mas não autenticado no Twitter/X.", file=sys.stderr)
        print("Para autenticar, execute manualmente fora da sessão do agente:", file=sys.stderr)
        print("1. xurl auth apps add seu-app --client-id ID --client-secret SECRET", file=sys.stderr)
        print("2. xurl auth oauth2 --app seu-app", file=sys.stderr)
        print("3. xurl auth default seu-app", file=sys.stderr)
        return False
        
    return True

def get_header_and_emoji(raw_header):
    """Maps markdown section headers to Twitter-optimized titles with emojis"""
    header = raw_header.lower().strip()
    if 'training' in header or 'treinamentos' in header or 'cursos' in header:
        return '🎓 5. TREINAMENTOS'
    elif header == 'ai' or header == 'ia' or 'inteligência artificial' in header or 'artificial intelligence' in header:
        return '🤖 1. IA'
    elif 'cloud' in header:
        return '☁️ 2. CLOUD COMPUTING'
    elif 'big tech' in header or 'grandes' in header:
        return '🏢 3. GRANDES EMPRESAS'
    elif 'financial' in header or 'mercado' in header:
        return '📈 4. MERCADO FINANCEIRO'
    elif 'jobs' in header or 'vagas' in header:
        return '💼 6. VAGAS'
    return None

def parse_newsletter(filepath):
    """Parses Hermes newsletter markdown file into sections and items"""
    path = Path(filepath)
    if not path.exists():
        print(f"❌ Erro: Arquivo {filepath} não encontrado.", file=sys.stderr)
        return None
        
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    sections = {}
    raw_sections = content.split('## ')
    
    # First split part might be main intro/text, let's ignore or parse if needed
    for raw in raw_sections[1:]:
        lines = raw.strip().split('\n')
        if not lines:
            continue
        raw_header = lines[0].strip()
        section_title = get_header_and_emoji(raw_header)
        if not section_title:
            continue
            
        section_content = '\n'.join(lines[1:])
        # Parse items: • {Title} - Source: {Source} - {Link}
        items = re.findall(r'[•\-]\s*(.*?)\s*-\s*Source:\s*(.*?)\s*-\s*(https?://[^\s\n)]+)', section_content)
        
        sections[section_title] = items
        
    return sections

def format_thread_tweets(sections):
    """Formats the sections into a list of tweet texts under 280 characters"""
    tweets = []
    
    # Tweet 1: Anchor Post
    now = datetime.now()
    # Detect period based on current hour
    hour = now.hour
    if hour < 12:
        period = "Manhã"
    elif hour < 18:
        period = "Tarde"
    else:
        period = "Noite"
        
    date_str = now.strftime('%d/%m/%Y')
    
    anchor_tweet = (
        f"📰 NEWSLETTER TECH & MARKET\n"
        f"Período: {period} - {date_str}\n\n"
        f"Confira as principais novidades de IA, Cloud, Big Tech, Mercado Financeiro, Treinamentos e Vagas de hoje! 👇 (Thread 🧵)"
    )
    tweets.append(anchor_tweet)
    
    # Process each section in standard order
    order = [
        '🤖 1. IA',
        '☁️ 2. CLOUD COMPUTING',
        '🏢 3. GRANDES EMPRESAS',
        '📈 4. MERCADO FINANCEIRO',
        '🎓 5. TREINAMENTOS',
        '💼 6. VAGAS'
    ]
    
    for section_name in order:
        items = sections.get(section_name, [])
        if not items:
            continue
            
        tweet_lines = [section_name]
        
        # We try to put up to 3 items in the tweet
        for title, source, link in items[:3]:
            # Clean title
            title = title.strip()
            source = source.strip()
            link = link.strip()
            
            item_line = f"• {title} ({source}) - {link}"
            temp_tweet = "\n\n".join(tweet_lines + [item_line])
            
            if calculate_x_length(temp_tweet) <= 275:
                tweet_lines.append(item_line)
            else:
                # If tweet is empty (only has header) and the first item is too long, we truncate
                if len(tweet_lines) == 1:
                    max_title_len = 275 - calculate_x_length(f"{section_name}\n\n•  ({source}) - {link}")
                    if max_title_len > 15:
                        truncated_title = title[:max_title_len - 3] + "..."
                        item_line = f"• {truncated_title} ({source}) - {link}"
                        tweet_lines.append(item_line)
                break
                
        tweets.append("\n\n".join(tweet_lines))
        
    return tweets

def post_thread(tweets):
    """Posts the thread to Twitter/X using xurl and returns a list of posted tweet IDs"""
    if not tweets:
        return []
        
    print(f"🚀 Iniciando publicação de Thread de {len(tweets)} tweets...")
    posted_ids = []
    
    # Post Anchor Tweet
    print(f"📝 Postando Tweet 1/{len(tweets)} (Âncora)...")
    code, stdout, stderr = run_command([XURL_PATH, "post", tweets[0]])
    if code != 0:
        print(f"❌ Erro ao postar tweet âncora: {stderr}", file=sys.stderr)
        return []
        
    try:
        response = json.loads(stdout)
        post_id = response['data']['id']
        posted_ids.append(post_id)
        print(f"✅ Tweet âncora postado com ID: {post_id}")
    except Exception as e:
        print(f"❌ Erro ao parsear resposta do Twitter para o tweet âncora: {e}", file=sys.stderr)
        print(f"Resposta bruta: {stdout}", file=sys.stderr)
        return []
        
    # Post Replies in Thread
    for i, tweet_text in enumerate(tweets[1:], start=2):
        parent_id = posted_ids[-1]
        print(f"📝 Postando Tweet {i}/{len(tweets)} (Respondendo ao ID {parent_id})...")
        
        code, stdout, stderr = run_command([XURL_PATH, "reply", parent_id, tweet_text])
        if code != 0:
            print(f"❌ Erro ao postar resposta {i}: {stderr}", file=sys.stderr)
            # We don't stop the loop here so we can try to publish as much as possible, or we could stop
            print("⚠️ Interrompendo a thread devido a falha de resposta.", file=sys.stderr)
            break
            
        try:
            response = json.loads(stdout)
            post_id = response['data']['id']
            posted_ids.append(post_id)
            print(f"✅ Tweet {i} postado com ID: {post_id}")
        except Exception as e:
            print(f"❌ Erro ao parsear resposta do Twitter para a resposta {i}: {e}", file=sys.stderr)
            print(f"Resposta bruta: {stdout}", file=sys.stderr)
            break
            
    return posted_ids

def main():
    if len(sys.argv) < 2:
        print("Uso: python3 publish_twitter.py <caminho_para_newsletter.md> [--dry-run]", file=sys.stderr)
        sys.exit(1)
        
    filepath = sys.argv[1]
    dry_run = "--dry-run" in sys.argv
    
    # Parse newsletter
    sections = parse_newsletter(filepath)
    if not sections:
        sys.exit(1)
        
    # Format tweets
    tweets = format_thread_tweets(sections)
    if not tweets:
        print("❌ Erro: Nenhum tweet pôde ser formatado a partir da newsletter.", file=sys.stderr)
        sys.exit(1)
        
    print("\n=== CONTEÚDO FORMATADO PARA O TWITTER ===")
    for i, tweet in enumerate(tweets, start=1):
        char_count = calculate_x_length(tweet)
        print(f"\n--- TWEET {i} ({char_count} chars) ---")
        print(tweet)
    print("=========================================\n")
    
    if dry_run:
        print("🧪 Executado em modo Dry Run. Nenhuma publicação real foi feita.")
        sys.exit(0)
        
    # Verify auth
    if not check_xurl_auth():
        print("⚠️ Pulando envio ao Twitter/X por falta de autenticação.", file=sys.stderr)
        print("Os dados foram formatados com sucesso, mas o xurl precisa de autorização ativa.", file=sys.stderr)
        sys.exit(0)  # We exit with 0 so it doesn't fail the cron job pipeline
        
    # Post
    posted_ids = post_thread(tweets)
    if posted_ids:
        print(f"🎉 Thread publicada com sucesso! {len(posted_ids)} tweets enviados.")
        print(f"Link da Thread: https://x.com/user/status/{posted_ids[0]}")
    else:
        print("❌ Falha ao publicar a Thread.")
        sys.exit(1)

if __name__ == '__main__':
    main()
