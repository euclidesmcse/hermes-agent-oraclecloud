#!/bin/bash
# Script de Backup do Hermes Agent e Configurações de Automação

BACKUP_DIR="/home/ubuntu/hermes-backup"
TAR_FILE="$BACKUP_DIR/hermes-configuration-backup.tar.gz"

echo "=== Iniciando Backup das Configurações do Hermes Agent ==="
mkdir -p "$BACKUP_DIR"

# Lista de itens a serem copiados para uma estrutura temporária para compactação limpa
TEMP_STAGE=$(mktemp -d)
mkdir -p "$TEMP_STAGE/hermes"
mkdir -p "$TEMP_STAGE/himalaya"
mkdir -p "$TEMP_STAGE/skills"

# 1. Copiar arquivos de configuração principal
if [ -f "/home/ubuntu/.hermes/config.yaml" ]; then
    cp "/home/ubuntu/.hermes/config.yaml" "$TEMP_STAGE/hermes/"
    echo "✔ Configurações do Hermes (config.yaml) salvas."
fi

if [ -f "/home/ubuntu/.hermes/.env" ]; then
    cp "/home/ubuntu/.hermes/.env" "$TEMP_STAGE/hermes/"
    echo "✔ Variáveis de ambiente e chaves (.env) salvas."
fi

# 2. Copiar memórias persistentes
if [ -d "/home/ubuntu/.hermes/memories" ]; then
    cp -r "/home/ubuntu/.hermes/memories" "$TEMP_STAGE/hermes/"
    echo "✔ Memórias persistentes (USER.md / MEMORY.md) salvas."
fi

# 3. Copiar agendador de Cron
if [ -d "/home/ubuntu/.hermes/cron" ]; then
    mkdir -p "$TEMP_STAGE/hermes/cron"
    if [ -f "/home/ubuntu/.hermes/cron/jobs.json" ]; then
        cp "/home/ubuntu/.hermes/cron/jobs.json" "$TEMP_STAGE/hermes/cron/"
    fi
    echo "✔ Agendamentos do cron local (jobs.json) salvos."
fi

# 4. Copiar banco de dados de sessões e histórico (opcional)
if [ -f "/home/ubuntu/.hermes/state.db" ]; then
    cp "/home/ubuntu/.hermes/state.db" "$TEMP_STAGE/hermes/"
    echo "✔ Banco de dados do Hermes (state.db) salvo."
fi

# 5. Copiar configurações de e-mail (Himalaya)
if [ -d "/home/ubuntu/.config/himalaya" ]; then
    cp -r "/home/ubuntu/.config/himalaya" "$TEMP_STAGE/himalaya/"
    echo "✔ Configurações de e-mail do Himalaya salvas."
fi

# 6. Copiar a pasta de docker-automation (excluindo os dados baixados e caches)
if [ -d "/home/ubuntu/.hermes/skills/docker-automation" ]; then
    mkdir -p "$TEMP_STAGE/skills/docker-automation"
    cp -r /home/ubuntu/.hermes/skills/docker-automation/* "$TEMP_STAGE/skills/docker-automation/" 2>/dev/null || true
    # Limpar pasta temporária de data se foi copiada
    rm -rf "$TEMP_STAGE/skills/docker-automation/data"
    echo "✔ Estrutura do Docker Automation (sem dados pesados) salva."
fi

# Criar o arquivo comprimido tar.gz
echo "Compactando arquivos em $TAR_FILE..."
tar -czf "$TAR_FILE" -C "$TEMP_STAGE" .

# Limpeza do estágio temporário
rm -rf "$TEMP_STAGE"

echo ""
echo "=========================================================="
echo "✅ Backup concluído com sucesso!"
echo "Arquivo de backup: $TAR_FILE"
echo "=========================================================="
echo "Dica: Guarde esse arquivo .tar.gz de forma segura fora desta VM."
