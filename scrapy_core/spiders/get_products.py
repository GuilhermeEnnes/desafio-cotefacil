#EXEMPLO
import argparse
import math
import scrapy
import json
import jwt
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

class GetProducts(scrapy.Spider):
    name = "get_products"

    def __init__(self, user, password, callback_url=None, *args, **kwargs):
        super(GetProducts, self).__init__(*args, **kwargs)
        self.user = user
        self.password = password
        self.callback_url = callback_url
        self.api_login_request = "https://peapi.servimed.com.br/api/usuario/login"  # Ajuste se necessário
        self.api_get_product_request = "https://peapi.servimed.com.br/api/carrinho/oculto?siteVersion=4.0.27"  # Exemplo
        self.cookies = None
        self.headers = None
        self.payload= None
        
    def start_requests(self):
        self.logger.info("Iniciando o processo de login...")
        formdata = {
            "usuario": self.user,
            "senha": self.password
        }
        
        yield scrapy.FormRequest(
            url=self.api_login_request,
            formdata=formdata,
            callback=self.after_login
        )
        
    def after_login(self, response):
        if response.status == 200:
            self.logger.info("Login realizado com sucesso!\n")
            self.logger.info("Iniciando a coleta de produtos...")
            try:
                active_cookies = response.headers.getlist('Set-Cookie')
                cookie_token = active_cookies[-1].decode('utf-8').split(';')[0].split('=')[1]
                self.cookies = {
                    "sessiontoken": cookie_token,
                    "accesstoken": cookie_token
                }
                
                access_token = jwt.decode(self.cookies['accesstoken'], options={"verify_signature": False})
                
                self.headers = {
                    'accesstoken': access_token['token'],
                    'content-type': 'application/json',
                }
            except Exception as e:
                self.logger.error(f"Erro ao processar cookies ou cabeçalhos: {e}")
                return

            self.payload = {
                "filtro": "",
                "pagina": 1,
                "registrosPorPagina": 100,
                "ordenarDecrescente": False,
                "colunaOrdenacao": "nenhuma",
                "clienteId": 267511,
                "tipoVendaId": 1,
                "fabricanteIdFiltro": 0,
                "pIIdFiltro": 0,
                "cestaPPFiltro": False,
                "codigoExterno": 0,
                "codigoUsuario": 22850,
                "promocaoSelecionada": "",
                "indicadorTipoUsuario": "CLI",
                "kindUser": 0,
                "xlsx": [],
                "principioAtivo": "",
                "master": False,
                "kindSeller": 0,
                "grupoEconomico": "",
                "users": [
                    518565,
                    267511
                ],
                "list": True
            }
            yield scrapy.Request(url=self.api_get_product_request,headers=self.headers,cookies=self.cookies, method='POST', body=json.dumps(self.payload),callback=self.build_product_list, dont_filter=True, errback=self.errback_function)
            
        else:
            self.logger.error("Falha no login. Verifique suas credenciais.")
            yield
    
    def build_product_list(self, response):
        self.logger.info("Construindo lista de produtos...")
        response_formatted = response.json()
        products = response_formatted.get('lista', [])
        
        for target_product in products:
            try:
                yield {
                    "gtin": str(target_product.get('codigoBarras', '')),
                    "codigo": str(target_product.get('id', '')),
                    "descricao": str(target_product.get('descricao', '')),
                    "preco_fabrica": float(target_product.get('valorBase', 0)),
                    "estoque": int(target_product.get('quantidadeEstoque', 0)),
                }
            except Exception as e:
                product_id = target_product.get('id', 'desconhecido')
                self.logger.error(
                    f"Erro ao processar o produto com ID {product_id}. Tipo de erro: {type(e).__name__}. Detalhes: {e}"
                )
                continue
        
        current_page = response_formatted.get('pagina', 1)
        total_records = response_formatted.get('totalRegistros', 0)
        record_per_page = response_formatted.get('registrosPorPagina', 1)
        total_pages = math.ceil(total_records / record_per_page)

        if(current_page <= total_pages):
            self.logger.info(f"Página {current_page} de {total_pages} processada. Total de registros: {total_records}.\n")
            self.logger.info(f"Iniciando processo da próxima página.")
            next_page = current_page + 1
            self.payload['pagina'] = next_page
            
            yield scrapy.Request(
                url=self.api_get_product_request,
                headers=self.headers,
                cookies=self.cookies,
                method='POST',
                body=json.dumps(self.payload),
                callback=self.build_product_list,
                dont_filter=True,
                errback=self.errback_function
            )
      
    def errback_function(self, failure):
        if hasattr(failure.value, 'response') and failure.value.response:
            status = getattr(failure.value.response, 'status', 'N/A')
            text = getattr(failure.value.response, 'text', 'N/A')
            self.logger.error(f"Erro ao processar a requisição: {status} - {text}")
        else:
            self.logger.error(f"Erro ao processar a requisição: {failure}")
            
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the GetProducts spider with user credentials.")
    parser.add_argument("--user", required=True, help="User email for authentication")
    parser.add_argument("--password", required=True, help="Password for authentication")
    parser.add_argument("--callback_url", required=False, help="Optional callback URL")
    args = parser.parse_args()
    
    settings = get_project_settings()
    process = CrawlerProcess(settings)
    process.crawl(GetProducts,  user=args.user, password=args.password, callback_url=args.callback_url)
    process.start(install_signal_handlers=False)
