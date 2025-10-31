import re
import scrapy

from textwrap import dedent

from app.db.database import get_db
from app.cruds.page_crud import PageCrud
from app.config import settings


class TextSpider(scrapy.Spider):
    """
    Scrapy spider to crawl a given domain (config.py), extract visible text content
    from pages, and store it in the database via the PageCrud

    Attributes:
        name: name that scrapy will use to find the spider
    """

    name = "text_spider"
    allowed_domains = [settings.DOMAIN]
    start_urls = [f"https://{settings.DOMAIN}/"]

    custom_settings = {
        "DEPTH_LIMIT": 0,
        "DOWNLOAD_DELAY": 0.5,
    }

    def __init__(self):
        super().__init__()

        self.total_chars = 0
        self.page_crud = PageCrud(get_db())
        self.page_crud.delete_all_pages()

    def parse(self, response):
        """
        Scrapy spider's default function to crawl and parse web page content
        """

        # Filter out JavaScript, CSS and html tags to get text
        texts = response.xpath(
            '//body//*[not(self::script or self::style or self::noscript)]/text()'
        ).getall()

        content = self._extract_content(texts)

        try:
            self._process_content_limit(len(content))
            self.page_crud.add_page(response.url, content)
        except Exception as e:
            print(f'[TextSpider] @parse. Unexpected error: {e}')

        links = response.css('a::attr(href)').getall()
        absolute_links = [response.urljoin(link) for link in links]

        for link in absolute_links:
            if self._is_internal_link(link):
                yield response.follow(link, callback=self.parse)

    def _is_internal_link(self, url: str) -> bool:
        """
        Checks if fetched links is a part of domain
        """
        return any(domain in url for domain in self.allowed_domains)

    def _extract_content(self, texts: list[str]) -> str:
        """
        Concatenate lists of string (default returned by Scrapy) into a single string removing indents and extra spaces
        """
        united_string = ' '.join(texts)
        united_string = re.sub(r'\s+', ' ', united_string).strip()
        return dedent(united_string)

    def _process_content_limit(self, content_len=0) -> bool:
        """
        Checks if saved content length is less than MAC_CONTENT_SIZE. Throws Exception if limit exceeded
        """
        self.total_chars += content_len
        if self.total_chars >= settings.MAX_CONTENT_SIZE:
            raise Exception('Limit exceeded')
