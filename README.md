# Backup & Recuperação de Desastres do Hermes Agent

Este repositório contém todo o ecossistema de automação do Hermes Agent rodando em sua máquina virtual da Oracle Cloud, além de scripts automatizados para garantir que nenhuma configuração, chave de API ou histórico de aprendizado/memória do agente seja perdido se houver uma falha catastrófica (crash) na VM.

---

## 📦 O que este ecossistema protege?
Ao realizar o backup utilizando as ferramentas deste repositório, você salva:
1. **Configurações Gerais (`config.yaml`):** O mapeamento de modelos e comportamentos padrões do seu agente.
2. **Variáveis de Ambiente (`.env`):** Todas as suas chaves e tokens de APIs secretas de LLMs (OpenAI, Gemini, Anthropic, etc.).
3. **Memórias do Agente (`memories/`):** Suas preferências de comunicação, regras de e-mails, fatos aprendidos e seu perfil pessoal de usuário (`USER.md` e `MEMORY.md`).
4. **Agendamentos de Cron (`cron/`):** Todos os disparos agendados de relatórios e newsletters.
5. **Configurações de E-mail (`himalaya`):** O mapeamento do seu cliente de e-mail local (Himalaya CLI) conectado ao seu Gmail (`euclidespns@gmail.com`).
6. **Automações de Docker (`skills/docker-automation`):** Os códigos-fontes, scrapers, newsletters, crawlers e configurações do `docker-compose` para o seu fluxo diário.

---

## ⏳ Como Criar um Backup (VM Atual)

Sempre que fizer alterações nas habilidades do agente ou quiser uma cópia de segurança recente, execute o script de backup na sua VM atual:

```bash
/home/ubuntu/hermes-agent-oraclecloud/scripts/backup.sh
```

### O que acontece em seguida?
Este script irá ler suas configurações ativas locais, sanitizá-las (excluindo arquivos temporários pesados e históricos desnecessários) e gerará um único arquivo compactado em:
📂 `/home/ubuntu/hermes-backup/hermes-configuration-backup.tar.gz`

> ⚠️ **IMPORTANTE:** Transfira este arquivo `.tar.gz` para o seu computador local para garantir a segurança em caso de queima ou perda da VM. Você pode baixar usando `scp` do seu terminal local ou ferramenta de SFTP de sua preferência:
> ```bash
> scp ubuntu@<IP_DA_VM>:/home/ubuntu/hermes-backup/hermes-configuration-backup.tar.gz ~/Downloads/
> ```

---

## 🔄 Como Restaurar Tudo em uma Nova VM (Passo a Passo)

Se a sua VM atual parar de funcionar de vez e você precisar provisionar uma nova instância do zero na Oracle Cloud, siga estas instruções exatamente na ordem abaixo:

### Passo 1: Preparar a Nova VM
1. Crie a nova instância Ubuntu Linux na Oracle Cloud.
2. Atualize o sistema e instale as dependências básicas:
   ```bash
   sudo apt update && sudo apt upgrade -y
   sudo apt install -y git curl tar docker.io docker-compose
   sudo usermod -aG docker ubuntu  # Recarregue a sessão SSH após rodar este comando
   ```

### Passo 2: Instalar o Hermes Agent
Instale o Hermes Agent na nova VM seguindo o procedimento padrão de inicialização (conforme as instruções oficiais).

### Passo 3: Configurar o Acesso SSH ao GitHub
1. Gere uma nova chave SSH na nova VM:
   ```bash
   ssh-keygen -t ed25519 -C "euclidespns@gmail.com"
   ```
2. Adicione a chave pública recém-gerada (`~/.ssh/id_ed25519.pub`) à sua conta do GitHub em **Settings -> SSH and GPG keys**.
3. Teste a conexão SSH com o GitHub:
   ```bash
   ssh -T git@github.com
   ```

### Passo 4: Clonar este Repositório na Nova VM
Com o acesso SSH liberado, clone o seu repositório de automação para a pasta home do usuário `ubuntu`:
```bash
git clone git@github.com:euclidesmcse/hermes-agent-oraclecloud.git /home/ubuntu/hermes-agent-oraclecloud
```

### Passo 5: Transferir o arquivo de Backup para a Nova VM
Envie o arquivo `hermes-configuration-backup.tar.gz` salvo em seu computador local para a pasta `/home/ubuntu/` na nova VM:
```bash
scp ~/Downloads/hermes-configuration-backup.tar.gz ubuntu@<IP_DA_NOVA_VM>:/home/ubuntu/
```

### Passo 6: Rodar o Script de Restauração Automatizado
Navegue até o repositório clonado e execute o script de restauração:
```bash
/home/ubuntu/hermes-agent-oraclecloud/scripts/restore.sh
```

**O que o script de restauração faz por debaixo dos panos?**
- Descompacta as credenciais `.env` e as configurações `config.yaml` do Hermes.
- Restaura seu histórico e base de memórias (`USER.md` e `MEMORY.md`), fazendo o agente "lembrar" de quem você é e das regras impostas imediatamente.
- Instala as configurações do Himalaya CLI para envio de e-mails.
- Move os diretórios dos workers do Docker de volta para as pastas de habilidades ativas (`~/.hermes/skills/`).
- Recria a estrutura interna necessária de diretórios temporários (`data/`, `output/`, `alerts/`) limpos de lixo.

### Passo 7: Reconstruir as Imagens do Docker
Agora que a estrutura do Docker foi recolocada no lugar correto pela restauração, navegue até a pasta correspondente e faça o build dos containers para estarem prontos:
```bash
cd /home/ubuntu/.hermes/skills/docker-automation
docker-compose build
```

### Passo 8: Verificar se tudo está Funcional
Verifique se os cronjobs do Hermes e as memórias do agente estão ativos na nova máquina:
```bash
hermes cronjob list
```

A restauração está pronta! O Hermes voltará a se comportar de forma inteligente exatamente do ponto em que parou, com o agendamento de newsletters e monitoramentos 100% preservados.
