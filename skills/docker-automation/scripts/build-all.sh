#!/bin/bash
# Build todas as imagens
set -e

SKILL_DIR="$(dirname "$0")"
cd "$SKILL_DIR"

echo "🔨 Build newsletter worker..."
docker-compose build hermes-newsletter

echo "🔨 Build stocks worker..."
docker-compose build hermes-stocks

echo "🔨 Build scraper worker..."
docker-compose build hermes-scraper

echo "✅ Build completo!"
docker images | grep hermes
