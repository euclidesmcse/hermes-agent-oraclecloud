#!/bin/bash
# Health Check Completo - Valida estrutura Docker + Ollama + Cron
# Uso: bash scripts/health-check.sh

set -e
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  HERMES HEALTH CHECK - PRÉ-REBOOT                            ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

ERRORS=0

# 1. Docker Engine
echo -n "1. Docker Engine......... "
if sudo systemctl is-active docker > /dev/null && docker ps > /dev/null 2>&1; then
    echo "✅ OK"
else
    echo "❌ FAIL"
    ((ERRORS++))
fi

# 2. Container Ollama
echo -n "2. Container Ollama...... "
if docker ps | grep -q ollama-llm; then
    echo "✅ OK"
else
    echo "❌ FAIL"
    ((ERRORS++))
fi

# 3. API Ollama
echo -n "3. API Ollama............ "
if curl -s http://localhost:11434/api/tags | grep -q "models"; then
    echo "✅ OK"
else
    echo "❌ FAIL"
    ((ERRORS++))
fi

# 4. Modelos Ollama
echo -n "4. Modelos Ollama........ "
MODELS=$(docker exec ollama-llm ollama list 2>/dev/null | grep -c "llama3.2" || echo 0)
if [ "$MODELS" -ge 2 ]; then
    echo "✅ OK ($MODELS modelos)"
else
    echo "❌ FAIL (apenas $MODELS modelos)"
    ((ERRORS++))
fi

# 5-7. Workers Docker
for WORKER in newsletter stocks scraper; do
    echo -n "$((5+WORKER-1)). ${WORK^} Worker........ "
    if docker images | grep -q "hermes-$WORKER"; then
        echo "✅ OK"
    else
        echo "❌ FAIL"
        ((ERRORS++))
    fi
done

# 8. Cron Jobs
echo -n "8. Cron Jobs (3)......... "
JOB1=$(hermes cronjob list 2>/dev/null | grep -c '"newsletter-daily-06h"')
JOB2=$(hermes cronjob list 2>/dev/null | grep -c '"newsletter-daily-13h"')
JOB3=$(hermes cronjob list 2>/dev/null | grep -c '"newsletter-daily-23h"')
if [ "$JOB1" -ge 1 ] && [ "$JOB2" -ge 1 ] && [ "$JOB3" -ge 1 ]; then
    echo "✅ OK"
else
    echo "❌ FAIL"
    ((ERRORS++))
fi

# 9. Skills
echo -n "9. Skills (docker, llm).. "
if [ -d ~/.hermes/skills/docker-automation ] && [ -d ~/.hermes/skills/llm-router ]; then
    echo "✅ OK"
else
    echo "❌ FAIL"
    ((ERRORS++))
fi

# 10. Permissões Docker
echo -n "10. Permissões Docker..... "
if [ "$(ls -la /var/run/docker.sock | awk '{print $1}')" = "srw-rw-rw-" ]; then
    echo "✅ OK"
else
    echo "❌ FAIL"
    ((ERRORS++))
fi

# 11. Usuário no grupo docker
echo -n "11. Grupo Docker.......... "
if groups $USER | grep -q docker; then
    echo "✅ OK"
else
    echo "❌ FAIL"
    ((ERRORS++))
fi

# 12. Espaço em disco
echo -n "12. Disco Livre (>50GB).... "
FREE=$(df -h ~ | tail -1 | awk '{print $4}' | sed 's/G//')
if [ "${FREE%.*}" -ge 50 ]; then
    echo "✅ OK (${FREE}G)"
else
    echo "❌ FAIL (${FREE}G)"
    ((ERRORS++))
fi

# 13. RAM Livre (>10GB)
echo -n "13. RAM Livre (>10GB)...... "
FREE_RAM=$(free -h | grep Mem | awk '{print $7}' | sed 's/Gi//')
if [ "${FREE_RAM%.*}" -ge 10 ]; then
    echo "✅ OK (${FREE_RAM}Gi)"
else
    echo "❌ FAIL (${FREE_RAM}Gi)"
    ((ERRORS++))
fi

# 14. Teste geração LLM
echo -n "14. Geração LLM........... "
RESPONSE=$(curl -s http://localhost:11434/api/generate \
  -d '{"model":"llama3.2:3b","prompt":"Oi","stream":false}' 2>/dev/null)
if echo "$RESPONSE" | grep -q "response"; then
    echo "✅ OK"
else
    echo "❌ FAIL"
    ((ERRORS++))
fi

# 15. Volumes Docker
echo -n "15. Volumes Docker........ "
if docker volume ls | grep -q "ollama-data"; then
    echo "✅ OK"
else
    echo "❌ FAIL"
    ((ERRORS++))
fi

echo ""
echo "══════════════════════════════════════════════════════════════"
if [ $ERRORS -eq 0 ]; then
    echo "✅ TODOS OS TESTES PASSARAM (15/15)"
    echo "══════════════════════════════════════════════════════════════"
    echo ""
    echo "🎉 SISTEMA 100% OPERACIONAL!"
    echo ""
    echo "Pronto para reboot. Após reiniciar:"
    echo "  1. Docker sobe automaticamente"
    echo "  2. Containers são reiniciados (restart: unless-stopped)"
    echo "  3. Cron jobs rodam nos horários agendados"
    echo "  4. Newsletter 23:00 será executada normalmente"
else
    echo "❌ $ERRORS TEST(S) FALHARAM"
    echo "══════════════════════════════════════════════════════════════"
    echo "Atenção: Existem problemas a serem resolvidos antes do reboot!"
fi
echo ""
