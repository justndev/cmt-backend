from sqlalchemy import Column, Integer, String, DateTime, func

from app.db.database import Base


class Page(Base):
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
