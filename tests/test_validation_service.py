import pytest
from unittest.mock import patch
from app.services.validation_service import ValidationService
from app.dtos.validation_response import ValidationResponse


class TestValidationService:
    """Unit tests for ValidationService"""

    @pytest.fixture
    def valid_question(self):
        return "What is the meaning of life?"

    # Happy path tests
    def test_validate_question_valid(self, valid_question):
        """Test that a valid question passes validation"""
        result = ValidationService.validate_question(valid_question)

        assert isinstance(result, ValidationResponse)
        assert result.is_valid is True

    def test_validate_question_at_min_length(self):
        """Test question at minimum length boundary"""
        with patch('app.services.validation_service.MIN_QUESTION_LENGTH', 5):
            question = "Hello"  # Exactly 5 characters
            result = ValidationService.validate_question(question)

            assert result.is_valid is True
            assert result.details == 'Question is valid'

    def test_validate_question_at_max_length(self):
        """Test question at maximum length boundary"""
        with patch('app.services.validation_service.MAX_QUESTION_LENGTH', 1000):
            question = "a" * 1000  # Exactly 1000 characters
            result = ValidationService.validate_question(question)

            assert result.is_valid is True
            assert result.details == 'Question is valid'

    # Empty/None tests
    def test_validate_question_empty_string(self):
        """Test that empty string fails validation"""
        result = ValidationService.validate_question("")

        assert result.is_valid is False
        assert result.details == 'No question provided'

    def test_validate_question_whitespace_only(self):
        """Test that whitespace-only string fails validation"""
        result = ValidationService.validate_question("   ")

        assert result.is_valid is False
        assert result.details == 'No question provided'

    def test_validate_question_tabs_and_newlines(self):
        """Test that tabs and newlines only fails validation"""
        result = ValidationService.validate_question("\t\n  \n\t")

        assert result.is_valid is False
        assert result.details == 'No question provided'

    def test_validate_question_none(self):
        """Test that None fails validation"""
        result = ValidationService.validate_question(None)

        assert result.is_valid is False
        assert result.details == 'No question provided'

    # Too short tests
    def test_validate_question_too_short(self):
        """Test that question below minimum length fails"""
        with patch('app.services.validation_service.MIN_QUESTION_LENGTH', 10):
            question = "Hi?"  # Only 3 characters
            result = ValidationService.validate_question(question)

            assert result.is_valid is False
            assert result.details

    def test_validate_question_one_char_below_min(self):
        """Test question one character below minimum"""
        with patch('app.services.validation_service.MIN_QUESTION_LENGTH', 5):
            question = "What"  # 4 characters
            result = ValidationService.validate_question(question)

            assert result.is_valid is False

    # Too long tests
    def test_validate_question_too_long(self):
        """Test that question above maximum length fails"""
        with patch('app.services.validation_service.MAX_QUESTION_LENGTH', 1000):
            question = "a" * 1001  # 1001 characters
            result = ValidationService.validate_question(question)

            assert result.is_valid is False
            assert result.details == 'Question is too long. Maximum length is 1000 characters'

    # Edge cases
    def test_validate_question_with_leading_trailing_spaces(self):
        """Test that spaces are trimmed for empty check but not for length"""
        with patch('app.services.validation_service.MIN_QUESTION_LENGTH', 5):
            question = "  What?  "  # Has content after strip
            result = ValidationService.validate_question(question)

            # Should pass because "What?" is content after strip
            assert result.is_valid is True

    def test_validate_question_unicode_characters(self):
        """Test question with unicode characters"""
        question = "Qu'est-ce que c'est? 你好吗？"
        result = ValidationService.validate_question(question)

        assert isinstance(result, ValidationResponse)
        # Should handle unicode properly

