from app.dtos.validation_response import ValidationResponse
from app.config import settings


MAX_QUESTION_LENGTH = settings.MAX_QUESTION_LENGTH
MIN_QUESTION_LENGTH = settings.MIN_QUESTION_LENGTH

class ValidationService:

    @staticmethod
    def validate_question(question: str) -> ValidationResponse:
        if not question or not question.strip():
            return ValidationResponse(False, 'No question provided')

        if len(question) < MIN_QUESTION_LENGTH:
            return ValidationResponse(False, f'Question is too short. Minimum length is {MIN_QUESTION_LENGTH} characters')
        
        if len(question) > MAX_QUESTION_LENGTH:
            return ValidationResponse(False, f'Question is too long. Maximum length is {MAX_QUESTION_LENGTH} characters')

        return ValidationResponse(True, 'Question is valid')
