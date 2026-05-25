#!/bin/bash
# Fix permanente para permissões do Docker
# Adiciona regra udev para garantir permissões corretas do socket

set -e

echo "🔧 Configurando permissões permanentes do Docker..."

# Cria regra udev
sudo bash -c 'cat > /etc/udev/rules.d/99-docker-permissions.rules << EOF
# Fix Docker socket permissions
KERNEL=="docker.sock", MODE="0666", GROUP="docker"
EOF'

# Reinicia serviço udev
sudo udevadm control --reload-rules
sudo udevadm trigger

# Garante permissão atual
sudo chmod 666 /var/run/docker.sock

echo "✅ Permissões configuradas!"
echo "ℹ️  Reinicie o sistema se ainda houver problemas após reboot"
