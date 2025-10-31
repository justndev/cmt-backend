import pytest
from unittest.mock import patch, MagicMock

from app.config import settings
from app.services.openai_service import OpenAIService
from app.dtos.ask_response import AskResponse, AskFormat


class TestOpenAIService:


    @pytest.fixture
    def mock_openai_key(self, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", settings.OPENAI_API_KEY)

    @pytest.fixture
    def service(self, mock_openai_key):
        return OpenAIService()

    @pytest.fixture
    def sample_data(self):
        return {
            "https://example.com/page1": "Content from page 1",
            "https://example.com/page2": "Content from page 2"
        }


    @patch('openai.responses.parse')
    def test_answer_question(self, mock_parse, service, sample_data):
        mock_response = MagicMock()
        mock_response.output_parsed = AskFormat(
            question="What is the content?",
            answer="The content is from page 1 and page 2",
            sources=["https://example.com/page1"]
        )
        mock_response.usage = MagicMock()
        mock_response.usage.input_tokens = 100
        mock_response.usage.output_tokens = 50

        mock_parse.return_value = mock_response

        result = service.answer_question("What is the content?", sample_data)

        assert isinstance(result, AskResponse)
        assert result.question == "What is the content?"
        assert result.answer == "The content is from page 1 and page 2"
        assert result.sources == ["https://example.com/page1"]
        assert result.usage.input_tokens == 100
        assert result.usage.output_tokens == 50

    @patch('openai.responses.parse')
    def test_answer_question_api_error(self, mock_parse, service, sample_data):
        mock_parse.side_effect = Exception("API Error")

        with pytest.raises(Exception) as exc_info:
            service.answer_question("Test question", sample_data)

        assert "API Error" in str(exc_info.value)