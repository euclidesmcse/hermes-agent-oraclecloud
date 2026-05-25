#!/bin/bash
# Verifica status da newsletter Docker
set -e

OUTPUT_DIR="$HOME/.hermes/skills/docker-automation/data/newsletter/output"
CRON_LOG="$HOME/.hermes/cron/logs"

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  Newsletter Docker - Status                                 ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Último arquivo gerado
if [ -d "$OUTPUT_DIR" ]; then
    LAST_FILE=$(ls -t "$OUTPUT_DIR"/*.md 2>/dev/null | head -1)
    if [ -n "$LAST_FILE" ]; then
        echo "✅ Último arquivo: $(basename $LAST_FILE)"
        echo "   Data: $(stat -c '%y' $LAST_FILE | cut -d'.' -f1)"
        echo "   Tamanho: $(wc -c < $LAST_FILE) bytes"
        echo ""
        echo "📰 Últimas manchetes:"
        head -6 "$LAST_FILE" | sed 's/^/   /'
    else
        echo "❌ Nenhum arquivo de newsletter encontrado"
    fi
else
    echo "❌ Diretório de output não existe"
fi

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  Cron Jobs Agendados                                        ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Lista cron jobs de newsletter
hermes cronjob list 2>/dev/null | grep -A 5 "newsletter" | head -20 || echo "Não foi possível listar cron jobs"

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  Próximos Horários                                          ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "🕐 06:00 - Newsletter da manhã"
echo "🕐 13:00 - Newsletter da tarde"
echo "🕐 23:00 - Newsletter da noite"
echo ""
echo "💡 Dica: Use 'hermes cronjob list' para ver todos os jobs"
echo ""
