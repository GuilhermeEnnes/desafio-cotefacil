from huey import RedisHuey
from run_spider import run_spider
import traceback
import logging
from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerProcess

from scrapy_core.spiders.create_order import CreateOrder

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('huey_worker.log'),  
    ]
)

logger = logging.getLogger(__name__)
huey = RedisHuey('scraper-tasks', host='localhost', port=6379)

@huey.task()
def process_products_scraping_task(data):
    try:
        logger.info(f"Processando scraping dos produtos com dados: {data}")
        user = data.get("usuario")
        password = data.get("senha")
        callback_url = data.get("callback_url")

        run_spider(user=user, password=password, callback_url=callback_url)
    except Exception as e:
        logger.error(f"Ocorreu um erro ao processar scraping dos produtos: {e}")
        traceback.print_exc()

    return "Spider finished processing."

@huey.task()
def process_create_order_scraping_task(data): 
    try:
        logger.info(f"Processando scraping do pedido com dados: {data}")
        user = data.get("usuario")
        password = data.get("senha")
        callback_url = data.get("callback_url")
        produtos = data.get("produtos")
        
        settings = get_project_settings()
        process = CrawlerProcess(settings)
        process.crawl(CreateOrder,  user=user, password=password, callback_url=callback_url, products_list=produtos)
        process.start(install_signal_handlers=False)
        
    except Exception as e:
        logger.error(f"Ocorreu um erro ao processar scraping do pedido: {e}")
        traceback.print_exc()

    return "Spider finished processing."