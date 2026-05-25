#!/bin/bash
# Executa newsletter worker
SKILL_DIR="$(dirname "$0")/.."
cd "$SKILL_DIR"

docker-compose run --rm hermes-newsletter "$@"
