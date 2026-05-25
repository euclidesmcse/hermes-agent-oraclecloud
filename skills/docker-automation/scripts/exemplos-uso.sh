#!/bin/bash
# =============================================================================
# EXEMPLO PRÁTICO: Como usar Docker Automation Workers no dia a dia
# =============================================================================

set -e
SKILL_DIR="$HOME/.hermes/skills/docker-automation"
cd "$SKILL_DIR"

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  Docker Automation Workers - Exemplos de Uso                ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# 1. Newsletter
echo "1️⃣  Newsletter Worker - Coleta notícias de RSS"
echo "   Comando: docker-compose run --rm hermes-newsletter"
echo "   Resultado: /data/newsletter/output/YYYY-MM-DD.md"
echo ""

# 2. Stocks  
echo "2️⃣  Stocks Worker - Template para monitoramento"
echo "   Comando: docker-compose run --rm hermes-stocks AAPL MSFT GOOGL"
echo "   Resultado: /data/stocks/alerts/YYYY-MM-DD_HHMM.md"
echo ""

# 3. Scraper
echo "3️⃣  Scraper Worker - Web scraping com Puppeteer"
echo "   Comando: docker-compose run --rm hermes-scraper https://example.com h1"
echo "   Resultado: /data/scraper/output/scrape_<timestamp>.json"
echo ""

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  Casos de Uso Reais                                         ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

echo "📰 CASO 1: Newsletter Diária Automatizada"
echo "-------------------------------------------"
echo "# 1. Worker coleta notícias automaticamente"
echo "docker-compose run --rm hermes-newsletter"
echo ""
echo "# 2. Hermes lê o output e formata para email"
echo "cat /data/newsletter/output/2026-05-25.md | himalaya send ..."
echo ""
echo "# 3. Economia: ~2000 tokens/dia → 0 tokens"
echo ""

echo "📈 CASO 2: Monitoramento de Ações"
echo "-----------------------------------"
echo "# 1. Worker prepara template"
echo "docker-compose run --rm hermes-stocks AAPL MSFT NVDA"
echo ""
echo "# 2. Hermes busca dados reais via MCP"
echo "mcp_yahoo_finance_get_tickers_info symbols=['AAPL','MSFT','NVDA']"
echo ""
echo "# 3. Hermes analisa e envia alerta se necessário"
echo ""

echo "🕸️ CASO 3: Scraping de Preços/Conteúdo"
echo "-----------------------------------------"
echo "# 1. Extrai título da página"
echo "docker-compose run --rm hermes-scraper https://exemplo.com 'h1.product-title'"
echo ""
echo "# 2. Extrai preço"
echo "docker-compose run --rm hermes-scraper https://loja.com/produto '.price'"
echo ""
echo "# 3. Resultado em JSON pronto para processamento"
echo ""

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  Integração com Cron Jobs do Hermes                         ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "# Exemplo: Cron job para newsletter às 06:00"
echo "hermes cronjob create --schedule='0 6 * * *' \\"
echo "  --name='newsletter-daily' \\"
echo "  --prompt='Rodar newsletter worker e enviar email'"
echo ""
echo "# Script do cron job executaria:"
echo "docker-compose -f ~/.hermes/skills/docker-automation/docker-compose.yml run --rm hermes-newsletter"
echo ""

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  Status dos Workers                                         ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
sudo docker images | grep hermes | awk '{printf "✅ %-30s %s (%s)\n", $1, $3, $6}'
echo ""
echo "💾 Dados salvos em: $SKILL_DIR/data/"
echo ""
