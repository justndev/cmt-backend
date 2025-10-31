import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")

    DOMAIN = 'tehisintellekt.ee'
    """
        Target domain to crawl.
        The spider will only crawl pages within this domain and its subdomains.
        Change this value to crawl a different website.
    """

    CHATGPT_MODEL = "gpt-4o-mini"

    MAX_QUESTION_LENGTH = 1000
    """
        Maximum allowed length for user questions in characters
    """

    MIN_QUESTION_LENGTH = 5
    """
        Minimum required length for user questions in characters
    """

    MAX_CONTENT_SIZE = 190000
    """
        Maximum total content size in characters across all crawled pages.
        The crawler will stop when this limit is reached.
    """

settings = Settings()
