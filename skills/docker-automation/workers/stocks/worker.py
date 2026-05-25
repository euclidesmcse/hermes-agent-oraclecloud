#!/usr/bin/env python3
"""
Stocks Worker - Monitora ações via Yahoo Finance MCP
Output: Markdown com preços e variações
"""

import sys
import os
from datetime import datetime
from pathlib import Path

# Output dir
OUTPUT_DIR = os.getenv('STOCKS_OUTPUT', '/data/stocks/alerts')

def main():
    # Symbols da linha de comando ou padrão
    if len(sys.argv) > 1:
        symbols = sys.argv[1:]
    else:
        symbols = ["AAPL", "MSFT", "GOOGL", "NVDA", "META", "TSLA"]
    
    print(f"Monitorando {len(symbols)} ações: {', '.join(symbols)}")
    
    # Nota: Este worker agora usa a MCP do Yahoo Finance
    # O Hermes Agent chama mcp_yahoo_finance_get_tickers_info diretamente
    # Este script apenas prepara o output
    
    output_path = Path(OUTPUT_DIR)
    output_path.mkdir(parents=True, exist_ok=True)
    
    date_str = datetime.now().strftime('%Y-%m-%d_%H%M')
    output_file = output_path / f"{date_str}.md"
    
    output = f"## Stock Monitor - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
    output += f"Symbols: {', '.join(symbols)}\n\n"
    output += "Para dados em tempo real, use:\n"
    output += "```bash\n"
    output += "mcp_yahoo_finance_get_tickers_info symbols=['AAPL', 'MSFT']\n"
    output += "```\n\n"
    output += "Ou chame o worker via Hermes:\n"
    output += "```bash\n"
    output += "docker-compose run --rm hermes-stocks AAPL MSFT GOOGL\n"
    output += "```\n"
    
    with open(output_file, 'w') as f:
        f.write(output)
    
    print(f"✅ Template salvo em: {output_file}")
    print(output)

if __name__ == '__main__':
    main()
