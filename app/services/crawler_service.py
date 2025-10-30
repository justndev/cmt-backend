# app/services/scraper_service.py
import subprocess
import threading
import time


class CrawlerService:
    def __init__(self, interval_hours: int = 25):
        self.is_running = False
        self.interval = interval_hours * 3600
        self.thread = threading.Thread(target=self._schedule_crawl, daemon=True)
        self.thread.start()

    def get_is_running(self) -> bool:
        return self.is_running

    def _run_crawl(self):
        print("Starting crawl")
        self.is_running = True
        try:
            result = subprocess.run(
                ["scrapy", "crawl", "text_spider"],
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )
            if result.returncode == 0:
                print("Crawl finished successfully")
            else:
                print(f"Crawl failed: {result.stderr}")
        except subprocess.TimeoutExpired:
            print("Crawl timed out")
        except Exception as e:
            print(f"[CRAWLER ERROR] {e}")
        finally:
            self.is_running = False

    def _schedule_crawl(self):
        while True:
            self._run_crawl()
            print(f"Next crawl in {self.interval/3600} hours")
            time.sleep(self.interval)

