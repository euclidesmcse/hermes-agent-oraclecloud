#!/bin/bash
# Executa stocks worker
SKILL_DIR="$(dirname "$0")/.."
cd "$SKILL_DIR"

docker-compose run --rm hermes-stocks "$@"
