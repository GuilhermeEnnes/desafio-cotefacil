from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy_core.spiders.get_products import GetProducts
import subprocess
import sys

def run_spider(user, password, callback_url):
    try:
        cmd = [
            sys.executable, "scrapy_core/spiders/get_products.py",
            "--user", user,
            "--password", password,
            "--callback_url", callback_url]
        result = subprocess.run(cmd, check=True)
        
        if result.returncode == 0:
            print(f"[INFO] Spider executado com sucesso para usuário: {user}")
        else:
            print(f"[ERROR] Ocorreu um erro ao executar o spider: {result.stderr}")  
    except Exception as e:
        import traceback
        print(f"[ERROR] Ocorreu um erro ao executar o spider: {e}")
        traceback.print_exc()
        
