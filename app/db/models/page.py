from sqlalchemy import Column, Integer, String, DateTime, func

from app.db.database import Base


class Page(Base):
    """
    Page ORM model that is used to store page information
    Attributes:
        id (int): Primary key, auto-incremented unique identifier
        url (str): Full URL of the crawled page including protocol
                  (e.g., "https://example.com/about")
                  Must be unique across all pages
        content (str): Extracted and cleaned text content from the page
                      Excludes scripts, styles, and other non-text elements
        created_at (datetime): Timestamp when the page was stored in the database
                              Automatically set to current time on creation
    """
    __tablename__ = "pages"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, index=True, nullable=False)
    content = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "url": self.url,
            "content": self.content,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
