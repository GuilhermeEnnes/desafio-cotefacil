import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tasks.worker import process_products_scraping_task


payload = {
    "usuario": "juliano@farmaprevonline.com.br",
    "senha": "a007299A",
    "callback_url": "https://desafio.cotefacil.net"
}

result = process_products_scraping_task(payload)
print(f"[INFO] Tarefa {result.task} enviada para fila com sucesso.")


