# Docker Automation Workers - Guia Rápido

## ✅ Instalação Completa

Docker e workers já estão instalados e configurados!

### Estrutura
```
~/.hermes/skills/docker-automation/
├── docker-compose.yml          # Configuração dos containers
├── workers/
│   ├── newsletter/             # Coleta notícias RSS
│   ├── stocks/                 # Monitora ações (usando MCP)
│   └── scraper/                # Web scraping
├── scripts/
│   ├── build-all.sh            # Build todas as imagens
│   ├── run-newsletter.sh       # Executa newsletter
│   ├── run-stocks.sh           # Executa stocks
│   ├── run-scraper.sh          # Executa scraper
│   └── cleanup.sh              # Limpeza
└── data/                       # Volumes de dados
```

## 🚀 Comandos Rápidos

### Newsletter (coleta notícias)
```bash
cd ~/.hermes/skills/docker-automation
docker-compose run --rm hermes-newsletter
```

### Scraper (web scraping)
```bash
docker-compose run --rm hermes-scraper https://example.com "h1"
```

### Limpeza
```bash
docker-compose down --rmi local
```

## 📊 Economia de Tokens

| Tarefa | Sem Docker | Com Docker | Economia |
|--------|-----------|-----------|----------|
| Newsletter diária | ~2000 tokens/dia | 0 | 100% |
| Monitoramento stocks | ~1500 tokens/run | 0 | 100% |
| Web scraping | ~3000 tokens/run | 0 | 100% |

**ROI:** 1-2 execuções já pagam o overhead de configuração.

## 🔧 Próximos Passos Sugeridos

1. **Newsletter Agendada**: Criar cron job para rodar às 06:00, 13:00, 23:00
2. **Stocks com MCP**: Usar `mcp_yahoo_finance` tools diretamente
3. **Scraper Avançado**: Adicionar mais seletores CSS e export formats
4. **Dashboard**: Prometheus + Grafana para métricas

## 📝 Exemplo: Cron Job de Newsletter

```bash
# ~/.hermes/cron/newsletter.job
{
  "action": "create",
  "schedule": "0 6 * * *",
  "prompt": "Rodar newsletter worker",
  "script": "~/.hermes/skills/docker-automation/scripts/run-newsletter.sh",
  "no_agent": true
}
```

## 🛠️ Troubleshooting

### Container não inicia
```bash
docker-compose logs hermes-newsletter
```

### Permissão Docker
```bash
sudo usermod -aG docker $USER
newgrp docker
```

### Limpar tudo
```bash
docker-compose down --rmi local --volumes
```
