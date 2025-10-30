import re
from textwrap import dedent
from typing import List

import scrapy

from app.db.database import SessionLocal
from app.services.page_crud import PageCrud


class TextSpider(scrapy.Spider):
    name = "text_spider"
    allowed_domains = ["tehisintellekt.ee"]
    start_urls = ["https://tehisintellekt.ee/"]

    custom_settings = {
        "DEPTH_LIMIT": 0,
        "DOWNLOAD_DELAY": 0.5,
    }

    def __init__(self):
        super().__init__()
        self.page_crud = PageCrud(SessionLocal())
        self.page_crud.reset_pages()

    def parse(self, response):
        texts = response.xpath(
            '//body//*[not(self::script or self::style or self::noscript)]/text()'
        ).getall()

        content = self._extract_content(texts)

        yield {
            "url": response.url,
            "content": content,
        }

        try:
            self.page_crud.add_page(response.url, content)
        except Exception as e:
            print(f'[TextSpider] @parse. Unexpected error: {e}')

        links = response.css('a::attr(href)').getall()
        absolute_links = [response.urljoin(link) for link in links]

        for link in absolute_links:
            if self._is_internal_link(link):
                yield response.follow(link, callback=self.parse)

    def _is_internal_link(self, url: str) -> bool:
        return any(domain in url for domain in self.allowed_domains)

    def _extract_content(self, texts: list[str]) -> str:
        united_string = ' '.join(texts)
        united_string = re.sub(r'\s+', ' ', united_string).strip()
        return dedent(united_string)
