from typing import List

from sqlalchemy.exc import SQLAlchemyError
from app.db.models.page import Page


class PageCrud:
    def __init__(self, db):
        """
        Initialize PageCrud with a database session

        Args:
            db: SQLAlchemy database session for executing queries
        """
        self.db = db

    def add_page(self, url: str, content: str) -> Page:
        """
        Add a new page to the database

        Args:
            url (str): The URL of the crawled page (must not be empty)
            content (str): The extracted text content from the page

        Returns:
            Page

        Raises:
            ValueError: If the URL is not valid
            SQLAlchemyError: If the database operation
        """
        if not url or not url.strip():
            raise ValueError("URL cannot be empty")
        try:
            page = Page(
                url=url,
                content=content,
            )
            self.db.add(page)
            self.db.commit()
            self.db.refresh(page)
            return page
        except SQLAlchemyError:
            self.db.rollback()
            print(f"[PageCrud] @add_page: Database error occurred")
            raise

    def get_all_pages(self) -> List[Page]:
        """
        Retrieve all pages from the database.

        Returns:
            List[Page]

        Raises:
            Exception: If the database query fails
        """
        try:
            return self.db.query(Page).all()
        except Exception:
            print(f"[PageCrud] @get_all_pages: Database error occurred")
            raise

    def delete_all_pages(self):
        """
        Delete all pages from the database.

        Returns:
            None

        Raises:
            SQLAlchemyError: If the delete operation or commit fails.
                           The transaction is automatically rolled back on error.
        """
        try:

            self.db.query(Page).delete()
            self.db.commit()
            return None
        except SQLAlchemyError:
            self.db.rollback()
            print(f"[PageCrud] @delete_all_pages: Database error occurred")
            raise
