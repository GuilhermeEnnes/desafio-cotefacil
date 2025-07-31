from asyncio.log import logger
import json
import requests
import scrapy
import os
import traceback
from scrapy.exporters import JsonItemExporter

class ProductPersistRouting:
    def open_spider(self, spider):
        self.items = []
        self.send_to_callback_url = bool(getattr(spider, 'callback_url', None))
        self.user = spider.user
        self.password = spider.password
        self.callback_url = spider.callback_url
        self.token = None
        
        try:
            if not self.send_to_callback_url:
                logger.info("Callback URL não fornecido, salvando localmente.")
                os.makedirs('output', exist_ok=True)
                self.file = open('output/servimed_products.json', 'wb')
                self.exporter = JsonItemExporter(
                    self.file, 
                    encoding='utf-8',
                    ensure_ascii=False,
                    indent=4
                )
                self.exporter.start_exporting()
        except Exception as e:
            logger.error(f"Erro ao criar o arquivo de saída: {e}")
            traceback.print_exc()

        

    def process_item(self, item, spider):
        if self.send_to_callback_url:
            self.items.append(item)
        else:
            self.exporter.export_item(item)
        
        return item

    def close_spider(self, spider):
        logger.info("Fechando o pipeline de roteamento de dados.")
        if self.send_to_callback_url and self.items:
            self.token = self.auth(self.callback_url)

            if self.token:
                self.send(self.items, self.callback_url)
        elif self.exporter:
            self.exporter.finish_exporting()
            self.file.close()
            spider.logger.info(f"Produtos salvos em: output/servimed_products.json")


    def auth(self, base_url):
        try:
            logger.info("Autenticando na API final")
            login_api_url = f"{base_url}/oauth/token"
            formdata={
                "grant_type": "password",
                "username": "jakson_teste_0",
                "password": "123456789"
            }
            
            headers = {
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            login_response = requests.post(
                url=login_api_url,
                data=formdata,
                headers=headers
            )
            
            if login_response.status_code == 200:
                logger.info("Autenticação realizada com sucesso")
                return login_response.json()["access_token"]
            return None
        except Exception as e:
            logger.error(f"Erro ao autenticar na API final: {e}")
            traceback.print_exc()
            return None

    def send(self, produtos, base_url):
        try:
            logger.info(f"Enviando {len(produtos)} produtos para o endpoint /produto")
            headers = {'Authorization': f'Bearer {self.token}'}
            response = requests.post(
                url=f"{base_url}/produto",
                json=produtos,
                headers=headers
            )
            if response.status_code == 201:
                logger.info(f"Produtos enviados com sucesso: {response.status_code} - {response.text}")
            else:
                logger.error(f"Erro ao enviar produtos: {response.status_code} - {response.text}")
            return
        except Exception as e:
            logger.error(f"Erro ao enviar produtos para a API final: {e}")
            traceback.print_exc()



