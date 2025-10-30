from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import load_only

from app.db.page import Page
from datetime import datetime
import json


class PageCrud:
    def __init__(self, db):
        self.db = db

    def reset_pages(self):
        """Delete all existing pages safely"""
        try:
            self.db.query(Page).delete()
            self.db.commit()
        except SQLAlchemyError as e:
            self.db.rollback()
            print(f"[DB ERROR] Failed to reset pages: {e}")
            raise

    def add_page(self, url: str, content: str):
        """Insert a single page with error handling"""
        try:
            page = Page(
                url=url,
                content=content,
                last_crawled=datetime.utcnow(),
            )
            self.db.add(page)
            self.db.commit()
            self.db.refresh(page)
            return page
        except SQLAlchemyError as e:
            self.db.rollback()
            print(f"[DB ERROR] Failed to add page ({url}): {e}")
            raise

    def get_all_pages(self):
        """Fetch all pages"""
        try:
            return self.db.query(Page).all()
        except Exception as e:
            print(f"[DB ERROR] Failed to fetch pages: {e}")
            raise

    def get_all_pages_light(self):
        """Fetch all pages but without the heavy 'content' field"""
        try:
            return self.db.query(Page).options(
                load_only(Page.id, Page.url, Page.last_crawled)).all()
        except SQLAlchemyError as e:
            print(f"[DB ERROR] Failed to fetch lightweight pages: {e}")
            raise
