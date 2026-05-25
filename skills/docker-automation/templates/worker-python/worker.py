# Template: Worker Python Genérico

Este template serve como base para criar novos workers Python ultra-leves.

## Estrutura Mínima

```
workers/meu-worker/
├── Dockerfile
├── worker.py
└── requirements.txt
```

## Dockerfile Template

```dockerfile
FROM python:3.12-alpine

WORKDIR /app

# Instalar dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código do worker
COPY worker.py .

# Comando padrão
CMD ["python", "/app/worker.py"]
```

## requirements.txt Template

```
# Adicione apenas o necessário para manter a imagem leve
# Exemplo:
requests==2.31.0
```

## worker.py Template

```python
#!/usr/bin/env python3
"""
Meu Worker - Descrição breve
Output: Formato de saída (Markdown, JSON, etc.)
"""

import os
import sys
from pathlib import Path

# Configuração via variáveis de ambiente
OUTPUT_DIR = os.getenv('OUTPUT_DIR', '/data/output')

def main():
    # Lógica do worker
    print("Executando worker...")
    
    # Preparar output
    output = "# Resultado\n\nConteúdo aqui\n"
    
    # Salvar resultado
    output_path = Path(OUTPUT_DIR)
    output_path.mkdir(parents=True, exist_ok=True)
    
    output_file = output_path / "resultado.md"
    with open(output_file, 'w') as f:
        f.write(output)
    
    print(f"✅ Salvo em: {output_file}")

if __name__ == '__main__':
    main()
```

## Adicionar ao docker-compose.yml

```yaml
services:
  meu-worker:
    build:
      context: ./workers/meu-worker
      dockerfile: Dockerfile
    volumes:
      - ./data/meu-worker:/data/output
    environment:
      - TZ=Europe/Lisbon
      - OUTPUT_DIR=/data/output
    entrypoint: ["python", "/app/worker.py"]
```

## Boas Práticas

1. **Mantenha leve:** Use apenas bibliotecas essenciais
2. **Sem estado:** Workers devem ser stateless, tudo via arquivos
3. **Logs claros:** Print no stdout para debugging
4. **Tratamento de erro:** Capture exceções e imprima no stderr
5. **Variáveis de ambiente:** Configure via .env ou docker-compose

## Exemplo de Uso

```bash
# Build
docker-compose build meu-worker

# Executar
docker-compose run --rm meu-worker

# Ver resultado
cat data/meu-worker/resultado.md
```

## Dicas para Economizar Tokens

1. **Input via arquivo:** Worker lê config de arquivo, não via LLM
2. **Output em Markdown:** Fácil do Hermes parsear depois
3. **Execução agendada:** Cron jobs não consomem tokens
4. **Reutilização:** Mesmo worker serve múltiplos propósitos
