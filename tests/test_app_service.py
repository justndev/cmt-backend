import pytest
from unittest.mock import Mock
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.dtos.ask_response import AskResponse
from app.services.app_service import AppService
from app.services.validation_service import ValidationService
from app.services.openai_service import OpenAIService
from app.cruds.page_crud import PageCrud


class TestAppService:

    @pytest.fixture
    def mock_session(self):
        return Mock(spec=Session)

    @pytest.fixture
    def mock_page_crud(self):
        return Mock(spec=PageCrud)

    @pytest.fixture
    def mock_validation_service(self):
        return Mock(spec=ValidationService)

    @pytest.fixture
    def mock_openai_service(self):
        return Mock(spec=OpenAIService)

    @pytest.fixture
    def app_service(self, mock_page_crud, mock_validation_service, mock_openai_service):
        service = AppService()
        service.page_crud = mock_page_crud
        service.validation_service = mock_validation_service
        service.openai_service = mock_openai_service
        return service

    @pytest.fixture
    def sample_pages(self):
        return [
            Mock(url="http://example.com/page1", content="Content of page 1"),
            Mock(url="http://example.com/page2", content="Content of page 2"),
        ]

    @pytest.fixture
    def sample_ask_response(self):
        return AskResponse(
            question="Test question",
            answer="Test answer",
            sources=["http://example.com/page1"],
            usage={"input_tokens": 10, "output_tokens": 5}
        )

    # Tests for get_source_info method
    class TestGetSourceInfo:
        def test_get_source_info_success(self, app_service, mock_page_crud, sample_pages):
            # Arrange
            mock_page_crud.get_all_pages.return_value = sample_pages
            expected_result = {
                "http://example.com/page1": "Content of page 1",
                "http://example.com/page2": "Content of page 2"
            }

            # Act
            result = app_service.get_source_info()

            # Assert
            mock_page_crud.get_all_pages.assert_called_once()
            assert result == expected_result

        def test_get_source_info_database_error(self, app_service, mock_page_crud):
            # Arrange
            mock_page_crud.get_all_pages.side_effect = Exception("Database connection failed")

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                app_service.get_source_info()

            assert exc_info.value.status_code == 500
            assert "Database connection failed" in str(exc_info.value.detail)
            mock_page_crud.get_all_pages.assert_called_once()

    # Tests for ask_question method
    class TestAskQuestion:
        def test_ask_question_success(self, app_service, mock_validation_service,
                                      mock_page_crud, mock_openai_service, sample_pages, sample_ask_response):
            # Arrange
            question = "What is the meaning of life?"
            mock_validation_result = Mock(is_valid=True)
            mock_validation_service.validate_question.return_value = mock_validation_result

            mock_page_crud.get_all_pages.return_value = sample_pages
            mock_openai_service.answer_question.return_value = sample_ask_response.model_dump()

            # Act
            result = app_service.ask_question(question)

            # Assert
            mock_validation_service.validate_question.assert_called_once_with(question)
            mock_page_crud.get_all_pages.assert_called_once()
            mock_openai_service.answer_question.assert_called_once()
            assert isinstance(result, AskResponse)
            assert result.question == sample_ask_response.question
            assert result.answer == sample_ask_response.answer

        def test_ask_question_validation_failed(self, app_service, mock_validation_service, mock_openai_service):
            # Arrange
            question = "Invalid question?"
            mock_validation_result = Mock(is_valid=False, details="Question is too short")
            mock_validation_service.validate_question.return_value = mock_validation_result

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                app_service.ask_question(question)

            assert exc_info.value.status_code == 400
            assert exc_info.value.detail == "Question is too short"
            mock_validation_service.validate_question.assert_called_once_with(question)
            # FIX: Use the correct mock - openai_service is on app_service, not validation_service
            mock_openai_service.answer_question.assert_not_called()

        def test_ask_question_no_pages_available(self, app_service, mock_validation_service, mock_page_crud,
                                                 mock_openai_service):
            # Arrange
            question = "What is the meaning of life?"
            mock_validation_result = Mock(is_valid=True)
            mock_validation_service.validate_question.return_value = mock_validation_result
            mock_page_crud.get_all_pages.return_value = []

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                app_service.ask_question(question)

            assert exc_info.value.status_code == 500
            # FIX: Check for the actual error detail format from your code
            assert "No information available" in str(exc_info.value.detail)
            mock_validation_service.validate_question.assert_called_once_with(question)
            mock_page_crud.get_all_pages.assert_called_once()
            mock_openai_service.answer_question.assert_not_called()

        def test_ask_question_openai_service_error(self, app_service, mock_validation_service,
                                                   mock_page_crud, mock_openai_service, sample_pages):
            # Arrange
            question = "What is the meaning of life?"
            mock_validation_result = Mock(is_valid=True)
            mock_validation_service.validate_question.return_value = mock_validation_result
            mock_page_crud.get_all_pages.return_value = sample_pages
            mock_openai_service.answer_question.side_effect = Exception("OpenAI API error")

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                app_service.ask_question(question)

            assert exc_info.value.status_code == 500
            assert "OpenAI API error" in str(exc_info.value.detail)
            mock_validation_service.validate_question.assert_called_once_with(question)
            mock_page_crud.get_all_pages.assert_called_once()
            mock_openai_service.answer_question.assert_called_once()

        def test_ask_question_database_error(self, app_service, mock_validation_service, mock_page_crud,
                                             mock_openai_service):
            # Arrange
            question = "What is the meaning of life?"
            mock_validation_result = Mock(is_valid=True)
            mock_validation_service.validate_question.return_value = mock_validation_result
            mock_page_crud.get_all_pages.side_effect = Exception("Database error")

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                app_service.ask_question(question)

            assert exc_info.value.status_code == 500
            assert "Database error" in str(exc_info.value.detail)
            mock_validation_service.validate_question.assert_called_once_with(question)
            mock_page_crud.get_all_pages.assert_called_once()
            mock_openai_service.answer_question.assert_not_called()