#!/bin/bash
# Exemplo de cron job para newsletter diária às 06:00
# Adiciona ao crontab do Hermes

cat << 'EOF' | hermes cronjob create --schedule="0 6 * * *" --name="newsletter-daily" --prompt="Executar worker de newsletter e enviar resultado por email"
docker-compose -f ~/.hermes/skills/docker-automation/docker-compose.yml run --rm hermes-newsletter
EOF

echo "✅ Cron job de newsletter criado!"
