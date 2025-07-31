from huey import RedisHuey
from run_spider import run_spider
import traceback
import logging

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
def process_scraping_task(data):
    try:
        logger.info(f"Processando tarefa de scraping com dados: {data}")
        user = data.get("usuario")
        password = data.get("senha")
        callback_url = data.get("callback_url")

        run_spider(user=user, password=password, callback_url=callback_url)
    except Exception as e:
        logger.error(f"Ocorreu um erro ao processar a tarefa de scraping: {e}")
        traceback.print_exc()

    return "Spider finished processing."