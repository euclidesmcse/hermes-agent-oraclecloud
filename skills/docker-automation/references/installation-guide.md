# Instalação e Configuração - Docker Automation Workers

## Resumo Executivo

**Objetivo:** Executar tarefas rotineiras do Hermes em containers Docker para economizar tokens em operações repetitivas.

**Arquitetura:**
- VM Oracle Cloud (Ubuntu ARM64)
- Docker Engine (~100MB RAM)
- 3 workers especializados (newsletter, stocks, scraper)
- Volumes compartilhados para input/output

## Instalação Passo a Passo

### 1. Instalar Docker na Oracle Cloud

```bash
# Atualizar repositórios
sudo apt-get update

# Instalar Docker e docker-compose
sudo apt-get install -y docker.io docker-compose

# Adicionar usuário ao grupo docker
sudo usermod -aG docker $USER
newgrp docker

# Verificar instalação
docker --version
docker ps
```

### 2. Estrutura de Diretórios

```bash
mkdir -p ~/.hermes/skills/docker-automation/{workers/{newsletter,stocks,scraper},scripts,data/{newsletter,stocks,scraper}}
```

### 3. Build das Imagens

```bash
cd ~/.hermes/skills/docker-automation
sudo docker-compose build
```

**Notas:**
- Build inicial requer `sudo` (permissões do Docker socket)
- Após build, execução não precisa de sudo (se usuário estiver no grupo docker)
- Imagens são cacheadas, rebuilds subsequentes são rápidos

### 4. Testar Workers

```bash
# Newsletter (coleta notícias RSS)
docker-compose run --rm hermes-newsletter

# Stocks (template para integração com MCP)
docker-compose run --rm hermes-stocks AAPL MSFT GOOGL

# Scraper (web scraping com Puppeteer)
docker-compose run --rm hermes-scraper https://example.com "h1"
```

## Troubleshooting

### Erro: Permission denied ao conectar no Docker

**Sintoma:**
```
PermissionError: [Errno 13] Permission denied
```

**Solução:**
```bash
# Adicionar usuário ao grupo docker
sudo usermod -aG docker $USER

# Re-login no grupo (ou logout/login)
newgrp docker

# Verificar
docker ps
```

### Erro: Cannot connect to Docker daemon

**Sintoma:**
```
Cannot connect to the Docker daemon at unix:///var/run/docker.sock
```

**Solução:**
```bash
# Verificar se serviço está rodando
sudo systemctl status docker

# Iniciar se necessário
sudo systemctl start docker
sudo systemctl enable docker
```

### Build falha com "no space left on device"

**Sintoma:**
```
no space left on device
```

**Solução:**
```bash
# Limpar imagens antigas
docker system prune -a

# Remover volumes órfãos
docker volume prune

# Verificar espaço
df -h
```

### Container não inicia (timeout)

**Sintoma:**
Container fica em "Creating" ou demora excessivamente

**Solução:**
```bash
# Verificar logs
docker-compose logs hermes-newsletter

# Forçar rebuild
docker-compose build --no-cache hermes-newsletter

# Verificar rede
docker network ls
```

## Métricas de Recursos

### Tamanho das Imagens
| Worker | Tamanho Comprimido | Tamanho em Disco |
|--------|-------------------|------------------|
| newsletter | 102MB | 24.7MB (runtime) |
| stocks | 92.1MB | 21.9MB (runtime) |
| scraper | 1.36GB | 375MB (runtime) |

### Consumo de CPU/Memória
- **Newsletter:** Pico de 50MB RAM, 5% CPU por 2-3 segundos
- **Stocks:** Pico de 40MB RAM, 3% CPU por 1-2 segundos
- **Scraper:** Pico de 400MB RAM, 15% CPU por 5-10 segundos

### Economia de Tokens
| Tarefa | Tokens/run | Runs/dia | Economia/dia |
|--------|-----------|----------|-------------|
| Newsletter | 2000 | 1 | 2000 tokens |
| Stocks | 1500 | 3 | 4500 tokens |
| Scraper | 3000 | 2 | 6000 tokens |
| **Total** | - | - | **12,500 tokens/dia** |

## Scripts de Exemplo

### build-all.sh
```bash
#!/bin/bash
set -e
cd ~/.hermes/skills/docker-automation
sudo docker-compose build
```

### run-newsletter.sh
```bash
#!/bin/bash
cd ~/.hermes/skills/docker-automation
docker-compose run --rm hermes-newsletter
```

### cleanup.sh
```bash
#!/bin/bash
# Remove containers parados
docker rm $(docker ps -aq -f status=exited) 2>/dev/null || true

# Remove imagens órfãs
docker image prune -f

# Opcional: volumes órfãos
# docker volume prune -f
```

## Próximos Passos

1. **Cron Jobs:** Configurar execução automática (06:00, 13:00, 23:00)
2. **MCP Integration:** Usar Yahoo Finance MCP para dados reais de stocks
3. **Alertas:** Configurar thresholds e notificações
4. **Dashboard:** Métricas de execução e economia

## Referências

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [Python Alpine Images](https://hub.docker.com/_/python)
- [Node.js Alpine Images](https://hub.docker.com/_/node)
