# Integração Docker + Hermes Cron Jobs

## Visão Geral

Este documento descreve o padrão de integração entre workers Docker e cron jobs do Hermes Agent.

## Arquitetura

```
VM Oracle (Ubuntu)
├── Docker Engine
│   ├── hermes-newsletter (worker)
│   ├── hermes-stocks (worker)
│   └── hermes-scraper (worker)
├── Hermes Agent
│   └── Cron Jobs (agendamento)
│       ├── newsletter-daily-06h
│       ├── newsletter-daily-13h
│       └── newsletter-daily-23h
└── Volumes Compartilhados
    └── /data/newsletter/output/
```

## Padrão de Comunicação

### 1. Worker Docker (Coleta Bruta)
```bash
docker-compose run --rm hermes-newsletter
# Output: /data/newsletter/output/YYYY-MM-DD.md
```

**Responsabilidade do worker:**
- Coletar dados brutos (RSS feeds, APIs)
- Formatar em markdown simples
- Salvar em volume compartilhado
- **NÃO** delegar, NÃO processar complexidade

### 2. Cron Job Hermes (Processamento Inteligente)
```json
{
  "job_id": "dda21d6e123a",
  "name": "newsletter-daily-06h",
  "schedule": "0 6 * * *",
  "skills": ["himalaya"],
  "prompt": "1. Rode worker Docker\n2. Leia output\n3. Formate newsletter\n4. Envie email"
}
```

**Responsabilidade do Hermes:**
- Acionar worker Docker (se necessário)
- Ler arquivo gerado
- Aplicar formatação complexa (6 seções, max 5 items, etc.)
- Enviar email via Himalaya CLI
- Confirmar entrega

## Configuração de Cron Jobs

### Job Simples (apenas Docker)
```bash
hermes cronjob create \
  --schedule="0 6 * * *" \
  --name="newsletter-daily-06h" \
  --prompt="Rode docker-compose run --rm hermes-newsletter e confirme"
```

### Job Composto (Docker + Processamento)
```bash
hermes cronjob create \
  --schedule="0 6 * * *" \
  --name="newsletter-daily-06h" \
  --skills='["himalaya"]' \
  --prompt="
1. Rode worker: docker-compose run --rm hermes-newsletter
2. Leia output em /data/newsletter/output/
3. Formate newsletter (6 seções, max 5 items)
4. Envie email para euclidespns@gmail.com
5. Confirme envio
"
```

## Troubleshooting

### Job não executa
```bash
# Verifica status
hermes cronjob list

# Testa execução manual
hermes cronjob run <job_id>

# Verifica logs
ls -lt ~/.hermes/cron/logs/
```

### Docker não inicia
```bash
# Verifica daemon
sudo systemctl status docker

# Testa container
docker-compose -f ~/.hermes/skills/docker-automation/docker-compose.yml run --rm hermes-newsletter
```

### Permissões
```bash
# Usuário no grupo docker
sudo usermod -aG docker $USER
newgrp docker

# Testa sem sudo
docker ps
```

## Melhores Práticas

### ✅ Faça
- Workers Docker "burros" (apenas coletam/formatam básico)
- Cron jobs com skills necessários (himalaya para email)
- Volumes em paths absolutos
- Teste manual antes de agendar
- Use `hermes cronjob run` para validar

### ❌ Não Faça
- Workers Docker com lógica complexa (consome tokens à toa)
- Cron jobs sem skills necessários
- Paths relativos (cron não tem seu cwd)
- Confiar em variáveis de ambiente do shell
- Agendar sem testar manualmente

## Economia de Tokens

| Tarefa | Abordagem Antiga | Abordagem Docker | Economia |
|--------|-----------------|------------------|----------|
| Newsletter | ~2000 tokens/execução | 0 tokens (worker) | 100% |
| Stocks Monitor | ~1500 tokens/execução | 0 tokens (worker) | 100% |
| Web Scraping | ~3000 tokens/execução | 0 tokens (worker) | 100% |

**ROI:** 1-2 execuções pagam o overhead de configuração.
