# RUNBOOK — Hermes Agent Oracle Cloud (backup & restore)

Este projeto é um **kit de backup/recuperação de desastres** do Hermes Agent. O guia completo está no [`README.md`](./README.md); este runbook resume a verificação operacional.

## 1. Gerar backup

```bash
/home/ubuntu/hermes-agent-oraclecloud/scripts/backup.sh
# saída: /home/ubuntu/hermes-backup/hermes-configuration-backup.tar.gz
```

## 2. Verificar o backup

```bash
ls -lh /home/ubuntu/hermes-backup/hermes-configuration-backup.tar.gz
tar tzf /home/ubuntu/hermes-backup/hermes-configuration-backup.tar.gz | head -30
```

Conferir que inclui: `config.yaml`, `.env`, `memories/` (`USER.md`, `MEMORY.md`), `cron/`, config do Himalaya, `skills/docker-automation`.

## 3. Transferir para fora da VM

```bash
scp ubuntu@<IP_DA_VM>:/home/ubuntu/hermes-backup/hermes-configuration-backup.tar.gz ~/Downloads/
```

> O backup contém **segredos** (`.env`, chaves de API). Guardar criptografado e fora do repositório.

## 4. Restaurar em nova VM

```bash
git clone git@github.com:euclidesmcse/hermes-agent-oraclecloud.git /home/ubuntu/hermes-agent-oraclecloud
# enviar o .tar.gz para /home/ubuntu/
/home/ubuntu/hermes-agent-oraclecloud/scripts/restore.sh
cd /home/ubuntu/.hermes/skills/docker-automation && docker-compose build
hermes cronjob list
```

## 5. Diagnóstico

| Sintoma | Ação |
|---|---|
| backup vazio | validar caminhos no `backup.sh` |
| restore falha | checar permissões e existência do `.tar.gz` |
| cron não aparece | `hermes cronjob list`; validar `cron/` restaurado |
| worker não sobe | rebuild do compose em `skills/docker-automation` |

## 6. Segurança

- `skills/docker-automation/.env` **não** é rastreado pelo Git (confirmado) — manter assim.
- Não versionar o `.tar.gz` de backup.
