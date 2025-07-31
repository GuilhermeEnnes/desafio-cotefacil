from urllib import response
import scrapy
import json
import jwt

class CreateOrder(scrapy.Spider):
    name = "create_order"
    custom_settings = {
        'ITEM_PIPELINES': {
            'scrapy_core.pipelines.confirm_create_order.ConfirmCreateOrder': 400,
        }
    }

    def __init__(self, user, password, callback_url, products_list, *args, **kwargs):
        super(CreateOrder, self).__init__(*args, **kwargs)
        self.user = user
        self.password = password
        self.callback_url = callback_url
        self.products_list = products_list
        self.api_login_request = "https://peapi.servimed.com.br/api/usuario/login"
        self.api_get_product_request = "https://peapi.servimed.com.br/api/carrinho/oculto?siteVersion=4.0.27"
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
            callback=self.find_product_by_id_list
        )
    
    def find_product_by_id_list(self, response):
        if response.status == 200:
            self.logger.info("Login realizado com sucesso!\n")
            self.logger.info("Iniciando a busca pelos produtos da lista...")
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
            
            self.logger.info("Construindo lista de produtos...")  
            for target_product in self.products_list:
                try:
                    self.payload = {
                        "filtro": str(target_product['codigo']),
                        "pagina": 1,
                        "registrosPorPagina": 1,
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
                    yield scrapy.Request(url=self.api_get_product_request,headers=self.headers,cookies=self.cookies, method='POST', body=json.dumps(self.payload),callback=self.process_product_response, dont_filter=True, errback=self.errback_function)
                except Exception as e:
                    product_id = target_product.get('id', 'desconhecido')
                    self.logger.error(
                        f"Erro ao processar o produto com ID {product_id}. Tipo de erro: {type(e).__name__}. Detalhes: {e}"
                    )
                    continue
        else:
            self.logger.error("Falha no login. Verifique suas credenciais.")
            yield
                   
    def process_product_response(self, response):
        formatted_response = response.json()
        products = formatted_response.get('lista', [])
        
        yield products[0] if products else None

    def errback_function(self, failure):
        if hasattr(failure.value, 'response') and failure.value.response:
            status = getattr(failure.value.response, 'status', 'N/A')
            text = getattr(failure.value.response, 'text', 'N/A')
            self.logger.error(f"Erro ao processar a requisição: {status} - {text}")
        else:
            self.logger.error(f"Erro ao processar a requisição: {failure}")