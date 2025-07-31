import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tasks.worker import process_create_order_scraping_task


payload = {
    "usuario": "juliano@farmaprevonline.com.br",
    "senha": "a007299A",
    "id_pedido": "1234",
    "produtos": [
        {
            "gtin": "1234567890123",
            "codigo": "441234",
            "quantidade": 1
        }
    ],
 "callback_url": "https://desafio.cotefacil.net"
}

result = process_create_order_scraping_task(payload)
print(f"[INFO] Tarefa {result.task} enviada para fila com sucesso.")


