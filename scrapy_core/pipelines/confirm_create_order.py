from asyncio.log import logger
import json
import requests
import scrapy
import os
import traceback
from scrapy.exporters import JsonItemExporter

class ConfirmCreateOrder:
    def open_spider(self, spider):
        self.items = []
        self.user = spider.user
        self.password = spider.password
        self.callback_url = spider.callback_url
        self.token = None     

    def process_item(self, item, spider):
        self.items.append(item)
        return item

    def close_spider(self, spider):
        logger.info("Fechando o pipeline de busca dos produtos do pedido.")
        if self.items:
            self.token = self.auth(self.callback_url)

            if self.token:
                self.create_order(self.items, self.callback_url)

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

    def create_order(self, products_to_order_list, base_url):
        try:
            logger.info(f"Criando pedido com os produtos: {products_to_order_list}")
            create_order_url = f"{base_url}/pedido"
            headers = {'Authorization': f'Bearer {self.token}'}
            create_order_response = self.fake_request_create_order(
                url=create_order_url,
                json={"produtos": products_to_order_list},
                headers=headers
            )
            
            if create_order_response['status'] == "pedido_realizado":
                logger.info(f"Pedido criado com sucesso")
                self.send_confirmation(base_url, create_order_response['codigo_confirmacao'], create_order_response['status'], create_order_response['id_pedido'])
            else:
                logger.error(f"Erro ao criar pedido")
        except Exception as e:
            logger.error(f"Erro ao criar pedido: {e}")
            traceback.print_exc()

    def fake_request_create_order(self, url, json, headers):
        return {
            "id_pedido": 12345,
            "codigo_confirmacao": "KOF2002",
            "status": "pedido_realizado"
        }

    def send_confirmation(self, base_url, codigo_confirmacao, status, id_pedido):
        try:
            logger.info(f"Enviando confirmação de pedido para o endpoint /pedido/:id")
            headers = {'Authorization': f'Bearer {self.token}'}
            data = {
                "codigo_confirmacao": codigo_confirmacao,
                "status": status
            }
            logger.info(f"Dados do pedido a serem enviados: {data}")
            
            response = requests.patch(
                url=f"{base_url}/pedido/{id_pedido}",
                json=data,
                headers=headers
            )
            response.status_code = 200
            
            if response.status_code == 200:
                logger.info(f"Criação de pedido confirmada com sucesso: {response.status_code}")
            else:
                logger.error(f"Erro ao confirmar criação de pedido: {response.status_code}")
            return
        except Exception as e:
            logger.error(f"Erro ao enviar produtos para a API final: {e}")
            traceback.print_exc()