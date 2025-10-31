from fastapi import HTTPException

from app.db.database import get_db
from app.dtos.ask_response import AskResponse
from app.cruds.page_crud import PageCrud
from app.services.openai_service import OpenAIService
from app.services.validation_service import ValidationService


class AppService:
    """
    Entry point from user request to app functionality. Handles exceptions from lower application layers and process business logic
    """

    def __init__(self):
        self.db = next(get_db())
        self.page_crud = PageCrud(self.db)
        self.validation_service = ValidationService()
        self.openai_service = OpenAIService()

    def get_source_info(self) -> dict[str, str]:
        """
        Retrieve all crawled pages and their content from the database.

        Returns:
            dict[str, str]
            Example: {"https://example.com": "Page content..."}

        Raises:
            HTTPException: 500 status code if database retrieval fails
        """
        try:
            pages_dict = {}
            pages = self.page_crud.get_all_pages()

            for page in pages:
                pages_dict[page.url] = page.content
            return pages_dict
        except Exception as e:
            print(f'[MainService] @get_source: {e}')
            raise HTTPException(status_code=500, detail=str(e))

    def ask_question(self, question: str) -> AskResponse:
        """
            Process a user question and generate an AI-powered answer based on crawled content.

            Returns:
                AskResponse

            Raises:
                HTTPException:
                    - 400 status code if question validation fails
                    - 500 status code if no pages are available in the database
                    - 500 status code if OpenAI processing fails or other unexpected errors occur
            """
        result = self.validation_service.validate_question(question)
        if not result.is_valid:
            raise HTTPException(status_code=400, detail=result.details)

        try:
            pages_dict = {}
            pages = self.page_crud.get_all_pages()

            if not pages:
                raise HTTPException(status_code=500, detail='No information available')

            for page in pages:
                pages_dict[page.url] = page.content

            result = self.openai_service.answer_question(question, pages_dict)
            return AskResponse.model_validate(result)
        except Exception as e:
            print(f'[MainService] @ask: {e}')
            raise HTTPException(status_code=500, detail=str(e))
