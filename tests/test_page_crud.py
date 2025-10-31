import pytest
from sqlalchemy.exc import SQLAlchemyError
from app.db.models.page import Page
from app.cruds.page_crud import PageCrud


class TestPageCrud:
    @pytest.fixture(autouse=True)
    def setup(self, setup_test_database):
        self.db = setup_test_database
        self.page_crud = PageCrud(self.db)

        yield

        self.db.close()

    def test_add_page_success(self):
        """Test adding a new page successfully"""
        # Arrange
        url = "https://example.com"
        content = "<html>Test Content</html>"

        # Act
        page = self.page_crud.add_page(url=url, content=content)

        # Assert
        assert page is not None
        assert page.id is not None
        assert page.url == url
        assert page.content == content
        assert page.created_at is not None

    def test_add_page_duplicate_url(self):
        """Test that adding duplicate URL raises an error"""
        # Arrange
        url = "https://example.com"
        content1 = "<html>Content 1</html>"
        content2 = "<html>Content 2</html>"

        # Act
        self.page_crud.add_page(url=url, content=content1)

        # Assert - should raise IntegrityError for duplicate URL
        with pytest.raises(SQLAlchemyError):
            self.page_crud.add_page(url=url, content=content2)

    def test_get_all_pages_empty(self):
        """Test getting all pages when database is empty"""
        # Act
        pages = self.page_crud.get_all_pages()

        # Assert
        assert pages == []
        assert len(pages) == 0

    def test_get_all_pages_multiple(self):
        """Test getting all pages with multiple entries"""
        # Arrange - add multiple pages
        pages_data = [
            ("https://example1.com", "<html>Content 1</html>"),
            ("https://example2.com", "<html>Content 2</html>"),
            ("https://example3.com", "<html>Content 3</html>"),
        ]

        for url, content in pages_data:
            self.page_crud.add_page(url=url, content=content)

        # Act
        pages = self.page_crud.get_all_pages()

        # Assert
        assert len(pages) == 3
        assert all(isinstance(page, Page) for page in pages)

        # Verify URLs are correct
        urls = [page.url for page in pages]
        assert "https://example1.com" in urls
        assert "https://example2.com" in urls
        assert "https://example3.com" in urls

    def test_reset_pages(self):
        """Test resetting/deleting all pages"""
        # Arrange - add some pages
        self.page_crud.add_page("https://example1.com", "<html>Content 1</html>")
        self.page_crud.add_page("https://example2.com", "<html>Content 2</html>")

        # Verify pages exist
        assert len(self.page_crud.get_all_pages()) == 2

        # Act
        self.page_crud.delete_all_pages()

        # Assert
        pages = self.page_crud.get_all_pages()
        assert len(pages) == 0

    def test_add_page_empty_url(self):
        """Test adding page with empty URL"""
        # Act & Assert
        with pytest.raises(Exception):
            self.page_crud.add_page(url="", content="<html>Content</html>")

    def test_add_page_empty_content(self):
        """Test adding page with empty content - should succeed"""
        # Arrange
        url = "https://example.com"

        # Act
        page = self.page_crud.add_page(url=url, content="")

        # Assert
        assert page is not None
        assert page.content == ""