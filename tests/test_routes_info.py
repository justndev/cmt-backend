import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException

from app.dtos.ask_response import AskResponse, Usage


class TestSourceInfoEndpoint:

    def test_get_source_info_success(self, client):
        """Test successful retrieval of source info"""
        # Use patch to mock the service in the actual route
        with patch('app.api.routes.info.AppService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            mock_service.get_source_info.return_value = {
                "https://example.com/page1": "Content 1",
                "https://example.com/page2": "Content 2"
            }

            response = client.get("/source_info")

            assert response.status_code == 200
            assert response.json() == {
                "https://example.com/page1": "Content 1",
                "https://example.com/page2": "Content 2"
            }

    def test_get_source_info_service_error(self, client):
        """Test get_source_info handles service errors"""
        with patch('app.api.routes.info.AppService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            # Make the mock raise the exception
            mock_service.get_source_info.side_effect = HTTPException(
                status_code=500,
                detail="Database connection failed"
            )

            response = client.get("/source_info")

            assert response.status_code == 500
            assert "Database connection failed" in response.json()["detail"]


class TestAskQuestionEndpoint:

    def test_ask_question_success(self, client):
        """Test successful question answering"""
        with patch('app.api.routes.info.AppService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            mock_response = AskResponse(
                question="What is AI?",
                answer="AI is artificial intelligence.",
                sources=["https://example.com"],
                usage=Usage(input_tokens=100, output_tokens=50)
            )
            mock_service.ask_question.return_value = mock_response

            response = client.post("/ask", json={"question": "What is AI?"})

            assert response.status_code == 200
            data = response.json()
            assert data["question"] == "What is AI?"
            assert data["answer"] == "AI is artificial intelligence."

    def test_ask_question_validation_error(self, client):
        """Test ask_question handles validation errors"""
        with patch('app.api.routes.info.AppService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            mock_service.ask_question.side_effect = HTTPException(
                status_code=400,
                detail="Invalid question format"
            )

            response = client.post("/ask", json={"question": ""})

            assert response.status_code == 400
            assert "Invalid question format" in response.json()["detail"]

    def test_ask_question_service_error(self, client):
        """Test ask_question handles service errors"""
        with patch('app.api.routes.info.AppService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            mock_service.ask_question.side_effect = HTTPException(
                status_code=500,
                detail="Internal server error"
            )

            response = client.post("/ask", json={"question": "What is AI?"})

            assert response.status_code == 500
            assert "Internal server error" in response.json()["detail"]