import pytest
from unittest.mock import Mock, patch
from fastapi import HTTPException

from app.dtos.ask_response import AskResponse, Usage
from app.dtos.validation_response import ValidationResponse
from app.services.main_service import MainService


class TesttMainService:
    @pytest.fixture
    def mock_page_crud(self):
        return Mock()

    @pytest.fixture
    def mock_validation_service(self):
        return Mock()

    @pytest.fixture
    def mock_openai_service(self):
        return Mock()

    @pytest.fixture
    def service(self, mock_page_crud, mock_validation_service, mock_openai_service):
        with patch('app.services.main_service.SessionLocal') as mock_session:
            mock_session.return_value = Mock()
            service = MainService()
            service.page_crud = mock_page_crud
            service.validation_service = mock_validation_service
            service.openai_service = mock_openai_service
            return service

    @pytest.fixture
    def mock_pages(self):
        page1 = Mock()
        page1.url = "https://example.com/page1"
        page1.content = "Content from page 1"

        page2 = Mock()
        page2.url = "https://example.com/page2"
        page2.content = "Content from page 2"

        return [page1, page2]

    # get_source_info tests
    def test_get_source_info_success(self, service, mock_page_crud, mock_pages):
        """Test successful retrieval of source info"""
        mock_page_crud.get_all_pages.return_value = mock_pages

        result = service.get_source_info()

        assert isinstance(result, dict)
        assert len(result) == 2
        assert result["https://example.com/page1"] == "Content from page 1"
        assert result["https://example.com/page2"] == "Content from page 2"
        mock_page_crud.get_all_pages.assert_called_once()

    def test_get_source_info_empty_pages(self, service, mock_page_crud):
        """Test get_source_info with no pages"""
        mock_page_crud.get_all_pages.return_value = []

        result = service.get_source_info()

        assert result == {}
        mock_page_crud.get_all_pages.assert_called_once()

    def test_get_source_info_single_page(self, service, mock_page_crud):
        """Test get_source_info with single page"""
        page = Mock()
        page.url = "https://example.com/single"
        page.content = "Single page content"
        mock_page_crud.get_all_pages.return_value = [page]

        result = service.get_source_info()

        assert len(result) == 1
        assert result["https://example.com/single"] == "Single page content"

    def test_get_source_info_database_error(self, service, mock_page_crud):
        """Test get_source_info handles database errors"""
        mock_page_crud.get_all_pages.side_effect = Exception("Database connection failed")

        with pytest.raises(HTTPException) as exc_info:
            service.get_source_info()

        assert exc_info.value.status_code == 500
        assert "Database connection failed" in str(exc_info.value.detail)

    def test_get_source_info_duplicate_urls(self, service, mock_page_crud):
        """Test get_source_info with duplicate URLs (last one wins)"""
        page1 = Mock()
        page1.url = "https://example.com/page"
        page1.content = "First content"

        page2 = Mock()
        page2.url = "https://example.com/page"
        page2.content = "Second content"

        mock_page_crud.get_all_pages.return_value = [page1, page2]

        result = service.get_source_info()

        assert len(result) == 1
        assert result["https://example.com/page"] == "Second content"

    # ask_question tests - validation
    def test_ask_question_invalid_question(self, service, mock_validation_service):
        """Test ask_question with invalid question"""
        mock_validation_service.validate_question.return_value = ValidationResponse(
            is_valid=False,
            details="Question is too short"
        )

        with pytest.raises(HTTPException) as exc_info:
            service.ask_question("Hi")

        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "Question is too short"
        mock_validation_service.validate_question.assert_called_once_with("Hi")

    def test_ask_question_validation_empty_question(self, service, mock_validation_service):
        """Test ask_question with empty question"""
        mock_validation_service.validate_question.return_value = ValidationResponse(
            is_valid=False,
            details="No question provided"
        )

        with pytest.raises(HTTPException) as exc_info:
            service.ask_question("")

        assert exc_info.value.status_code == 400
        assert "No question provided" in exc_info.value.detail

    # ask_question tests - no pages available
    def test_ask_question_no_pages(self, service, mock_validation_service, mock_page_crud):
        """Test ask_question when no pages are available"""
        mock_validation_service.validate_question.return_value = ValidationResponse(
            is_valid=True,
            details=""
        )
        mock_page_crud.get_all_pages.return_value = {}

        with pytest.raises(HTTPException) as exc_info:
            service.ask_question("What is AI?")

        assert exc_info.value.status_code == 500

    # ask_question tests - success
    def test_ask_question_success(
            self, service, mock_validation_service, mock_page_crud,
            mock_openai_service, mock_pages
    ):
        """Test successful ask_question flow"""
        question = "What is the content?"

        # Setup mocks
        mock_validation_service.validate_question.return_value = ValidationResponse(
            is_valid=True,
            details=""
        )
        mock_page_crud.get_all_pages.return_value = mock_pages

        mock_answer = AskResponse(
            question=question,
            answer="The content is from page 1 and page 2",
            sources=["https://example.com/page1", "https://example.com/page2"],
            usage=Usage(input_tokens=100, output_tokens=50)
        )
        mock_openai_service.answer_question.return_value = mock_answer

        # Execute
        result = service.ask_question(question)

        # Assertions
        assert isinstance(result, AskResponse)
        assert result.question == question
        assert result.answer == "The content is from page 1 and page 2"
        assert len(result.sources) == 2
        assert result.usage.input_tokens == 100
        assert result.usage.output_tokens == 50

        # Verify method calls
        mock_validation_service.validate_question.assert_called_once_with(question)
        mock_page_crud.get_all_pages.assert_called_once()
        mock_openai_service.answer_question.assert_called_once()

        # Verify OpenAI was called with correct data
        call_args = mock_openai_service.answer_question.call_args
        assert call_args[0][0] == question
        pages_dict = call_args[0][1]
        assert "https://example.com/page1" in pages_dict
        assert "https://example.com/page2" in pages_dict

    def test_ask_question_builds_correct_pages_dict(
            self, service, mock_validation_service, mock_page_crud,
            mock_openai_service, mock_pages
    ):
        """Test that ask_question builds pages_dict correctly"""
        mock_validation_service.validate_question.return_value = ValidationResponse(
            is_valid=True,
            details=""
        )
        mock_page_crud.get_all_pages.return_value = mock_pages
        mock_openai_service.answer_question.return_value = AskResponse(
            question="test",
            answer="answer",
            sources=[],
            usage=Usage(input_tokens=10, output_tokens=10)
        )

        service.ask_question("test question")

        # Check the pages_dict passed to OpenAI
        call_args = mock_openai_service.answer_question.call_args[0]
        pages_dict = call_args[1]

        assert pages_dict["https://example.com/page1"] == "Content from page 1"
        assert pages_dict["https://example.com/page2"] == "Content from page 2"

    # ask_question tests - error handling
    def test_ask_question_page_crud_error(
            self, service, mock_validation_service, mock_page_crud
    ):
        """Test ask_question handles page_crud errors"""
        mock_validation_service.validate_question.return_value = ValidationResponse(
            is_valid=True,
            details=""
        )
        mock_page_crud.get_all_pages.side_effect = Exception("Database error")

        with pytest.raises(HTTPException) as exc_info:
            service.ask_question("What is AI?")

        assert exc_info.value.status_code == 500
        assert "Database error" in str(exc_info.value.detail)

    def test_ask_question_openai_error(
            self, service, mock_validation_service, mock_page_crud,
            mock_openai_service, mock_pages
    ):
        """Test ask_question handles OpenAI errors"""
        mock_validation_service.validate_question.return_value = ValidationResponse(
            is_valid=True,
            details=""
        )
        mock_page_crud.get_all_pages.return_value = mock_pages
        mock_openai_service.answer_question.side_effect = Exception("OpenAI API error")

        with pytest.raises(HTTPException) as exc_info:
            service.ask_question("What is AI?")

        assert exc_info.value.status_code == 500
        assert "OpenAI API error" in str(exc_info.value.detail)

    def test_ask_question_openai_timeout(
            self, service, mock_validation_service, mock_page_crud,
            mock_openai_service, mock_pages
    ):
        """Test ask_question handles OpenAI timeout"""
        mock_validation_service.validate_question.return_value = ValidationResponse(
            is_valid=True,
            details=""
        )
        mock_page_crud.get_all_pages.return_value = mock_pages
        mock_openai_service.answer_question.side_effect = TimeoutError("Request timeout")

        with pytest.raises(HTTPException) as exc_info:
            service.ask_question("What is AI?")

        assert exc_info.value.status_code == 500

    # Integration-like tests (still mocked but testing full flow)
    def test_ask_question_full_flow(
            self, service, mock_validation_service, mock_page_crud,
            mock_openai_service
    ):
        """Test complete ask_question flow with all steps"""
        question = "Explain AI in simple terms"

        # Setup all mocks
        mock_validation_service.validate_question.return_value = ValidationResponse(
            is_valid=True,
            details=""
        )

        page = Mock()
        page.url = "https://ai-guide.com"
        page.content = "AI is artificial intelligence..."
        mock_page_crud.get_all_pages.return_value = [page]

        expected_response = AskResponse(
            question=question,
            answer="AI is a field of computer science...",
            sources=["https://ai-guide.com"],
            usage=Usage(input_tokens=150, output_tokens=75)
        )
        mock_openai_service.answer_question.return_value = expected_response

        # Execute
        result = service.ask_question(question)

        # Verify all components were called in order
        assert mock_validation_service.validate_question.called
        assert mock_page_crud.get_all_pages.called
        assert mock_openai_service.answer_question.called

        # Verify result
        assert result == expected_response

    # Parametrized tests
    @pytest.mark.parametrize("question,is_valid,error_detail", [
        ("", False, "No question provided"),
        ("Hi", False, "Question is too short"),
        ("a" * 1001, False, "Question is too long"),
    ])
    def test_ask_question_validation_scenarios(
            self, service, mock_validation_service, question, is_valid, error_detail
    ):
        """Test various validation scenarios"""
        mock_validation_service.validate_question.return_value = ValidationResponse(
            is_valid=is_valid,
            details=error_detail
        )

        with pytest.raises(HTTPException) as exc_info:
            service.ask_question(question)

        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == error_detail