# Desafio CoteFácil
    O objetivo deste desafio é criar um sistema de scraping e automação de pedidos para a plataforma CoteFácil usando o site da ServiMed. Para concluí-lo, foram usadas as seguintes tecnologias:
- Scrapy
- Huey
- Redis
- Python (versão 3.10.6)

## Instalação
1. **Clone o repositório**:
   ```
   git clone https://github.com/usuario/desafio-cotefacil.git
    cd desafio-cotefacil
    ```
2. **Instale as dependências**:
    ```
    pip install -r requirements.txt
    ```


## Configuração do Ambiente

1. **Redis**: Para rodar o Redis, utilize o seguinte comando:
   ```
   docker run -d --name redis-celery -p 6379:6379 redis:7
   ```

2. **Huey**: Para rodar o Huey, utilize o seguinte comando:
   ```
   huey_consumer.py tasks.worker.huey
   ```

3. **Spider**: Para rodar o spider manualmente com save local, utilize o seguinte comando:
   ```
   python scrapy_core/spiders/get_products.py --user "NOME-DO-USUÁRIO" --password "SENHA-DO-USUÁRIO"
   ```
4. **Producers**:
   - Para rodar o spider via mensageiria e enviar os produtos para a api de callback, utilize o producer de pegar produtos:
   ```
   python producers/get_products.py
   ```
   - Para disparar a mensagem que irá acionar o spider responsável por simular um pedido no site e enviar e enviar o código de confirmação do pedido realizado, utilize o producer de criar pedido:
   ```
   python producers/create_order.py
   ```

## Estrutura do Projeto
- `scrapy_core`: Contém o código do Scrapy, incluindo spiders e pipelines.
- `producers`: Contém os scripts que produzem mensagens para o Redis.
- `tasks`: Contém as tarefas que o Huey orquestra assíncronamente ao consumir as mensagens do Redis.
- `requirements.txt`: Lista as dependências do projeto.
- `spiders`: Contém os spiders do Scrapy.
- `pipelines`: Contém os pipelines do Scrapy, incluindo o pipeline de confirmação de criação de pedidos.

