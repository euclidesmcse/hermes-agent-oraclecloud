#!/bin/bash
# Script de Restauração das Configurações do Hermes Agent em uma Nova VM

BACKUP_FILE="/home/ubuntu/hermes-configuration-backup.tar.gz"

echo "=== Iniciando Restauração das Configurações do Hermes Agent ==="
echo ""

# Verificar se o arquivo de backup existe
if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ Erro: Arquivo de backup não encontrado em: $BACKUP_FILE"
    echo "Envie o arquivo 'hermes-configuration-backup.tar.gz' para a pasta '/home/ubuntu/' e tente novamente."
    exit 1
fi

# Criar os diretórios necessários na nova VM
mkdir -p "/home/ubuntu/.hermes"
mkdir -p "/home/ubuntu/.config"

# Extrair os arquivos em um diretório temporário
TEMP_STAGE=$(mktemp -d)
tar -xzf "$BACKUP_FILE" -C "$TEMP_STAGE"

# 1. Restaurar configurações principais do Hermes
if [ -d "$TEMP_STAGE/hermes" ]; then
    cp -r $TEMP_STAGE/hermes/* "/home/ubuntu/.hermes/"
    echo "✔ Configurações principais e variáveis (.env/config.yaml) restauradas."
fi

# 2. Restaurar configurações do Himalaya (Email)
if [ -d "$TEMP_STAGE/himalaya" ]; then
    mkdir -p "/home/ubuntu/.config/himalaya"
    cp -r $TEMP_STAGE/himalaya/* "/home/ubuntu/.config/himalaya/"
    echo "✔ Configurações de envio de e-mail (Himalaya) restauradas."
fi

# 3. Restaurar as Skills personalizadas (como o docker-automation)
if [ -d "$TEMP_STAGE/skills/docker-automation" ]; then
    mkdir -p "/home/ubuntu/.hermes/skills/docker-automation"
    cp -r $TEMP_STAGE/skills/docker-automation/* "/home/ubuntu/.hermes/skills/docker-automation/"
    
    # Recriar estrutura de diretórios de dados necessários para os workers
    mkdir -p "/home/ubuntu/.hermes/skills/docker-automation/data"/{newsletter/output,scraper/output,stocks/alerts}
    echo "✔ Estrutura do Docker Automation restaurada com sucesso."
fi

# Limpeza
rm -rf "$TEMP_STAGE"

echo ""
echo "=========================================================="
echo "✅ Restauração concluída com sucesso na nova VM!"
echo "=========================================================="
echo "Próximos passos recomendados:"
echo "1. Instalar o Docker na nova VM (caso ainda não esteja instalado)."
echo "2. Fazer o build dos containers do docker-automation:"
echo "   cd ~/.hermes/skills/docker-automation && docker-compose build"
echo "3. Verificar o status dos cronjobs locais do Hermes:"
echo "   hermes cronjob list"
echo "=========================================================="
