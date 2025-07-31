BOT_NAME = "servimed_crawler"
SPIDER_MODULES = ["scrapy_core.spiders"]
NEWSPIDER_MODULE = "scrapy_core.spiders"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
DOWNLOAD_DELAY = 1
LOG_LEVEL = "DEBUG" #"INFO","DEBUG","CRITICAL","ERROR","WARNING"
RETRY_ENABLED = True
RETRY_TIMES = 3
DOWNLOAD_TIMEOUT = 30
ITEM_PIPELINES = {
    'scrapy_core.pipelines.product_persist_routing.ProductPersistRouting': 300,
    'scrapy_core.pipelines.confirm_create_order.ConfirmCreateOrder': 400,    
}


