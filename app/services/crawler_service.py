import subprocess
import threading


class CrawlerService:
    """
         Runs text_spider.py in subprocess for web crawling once when application is started
    """
    def __init__(self):
        self.thread = threading.Thread(target=self._run_crawl, daemon=True)
        self.thread.start()

    def _run_crawl(self):
        try:
            result = subprocess.run(
                ["scrapy", "crawl", "text_spider"],
                capture_output=True,
                text=True,
                timeout=3600,
            )
            if result.returncode == 0:
                print("[CrawlerService] Crawl finished successfully")
            else:
                print(f"[CrawlerService] Crawl failed: {result.stderr}")
        except subprocess.TimeoutExpired:
            print("[CrawlerService] Crawl timed out")
        except Exception as e:
            print(f"[CrawlerService] Unexpected error: {e}")
