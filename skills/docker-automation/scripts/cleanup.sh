#!/bin/bash
# Cleanup: remove containers parados e imagens órfãs
set -e

echo "🧹 Limpando containers parados..."
docker rm $(docker ps -aq -f status=exited) 2>/dev/null || echo "Nenhum container para remover"

echo "🧹 Limpando imagens órfãs..."
docker image prune -f

echo "🧹 Limpando volumes órfãos (opcional)..."
# docker volume prune -f

echo "✅ Limpeza completa!"
docker system info | grep -E "Images|Containers|Volumes"
