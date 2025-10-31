from typing import Dict

from fastapi import APIRouter, Depends
from app.dtos.ask_request import AskRequest
from app.dtos.ask_response import AskResponse
from app.services.app_service import AppService

router = APIRouter()


# ============================================================================
# Info controller for web information related requests
# ============================================================================


def get_app_service():
    """
    Dependency injection factory for AppService.
    """
    return AppService()


@router.get("/source_info")
def get_source_info(service: AppService = Depends(get_app_service)) -> Dict[str, str]:
    """
    Retrieve all crawled pages and their content.

    Returns a dictionary mapping each crawled URL to its extracted text content.
    This endpoint is useful for:
    - Debugging: Verify what content was crawled
    - Monitoring: Check if the crawler has completed
    - Inspection: Review the data available for question answering

    Args:
        service (AppService): Injected application service (automatic via Depends)

    Returns:
        Dict[str, str]: Dictionary mapping URLs to their text content.
            Example:
            {
                "https://tehisintellekt.ee/": "Homepage content...",
                "https://tehisintellekt.ee/about": "About page content...",
                "https://tehisintellekt.ee/services": "Services content..."
            }

    Raises:
        HTTPException: 500 status code if database retrieval fails

    Example:
        GET /source_info

        Response:
        {
            "https://example.com/": "Welcome to our site...",
            "https://example.com/contact": "Contact us at..."
        }
    """
    return service.get_source_info()


@router.post("/ask")
async def ask_question(
        request_data: AskRequest,
        service: AppService = Depends(get_app_service)
) -> AskResponse:
    """
    Answer a user question based on crawled website content

    Args:
        request_data (AskRequest): Request body containing:
            - question (str): The user's question (5-1000 characters)
        service (AppService): Injected application service (automatic via Depends)

    Returns:
        AskResponse: Structured response containing:
            - question (str): The original question
            - answer (str): AI-generated answer in the same language as the question
            - sources (list[str]): URLs of pages used to answer the question
            - usage (Usage): Token usage statistics
                - input_tokens (int): Tokens consumed in the request
                - output_tokens (int): Tokens generated in the response

    Raises:
        HTTPException:
            - 400 status code if question validation fails:
                - Question is empty or only whitespace
                - Question is shorter than 5 characters
                - Question is longer than 1000 characters
            - 500 status code if no crawled content is available
            - 500 status code if OpenAI API call fails

    Example:
        POST /ask
        {
            "question": "What services does the company offer?"
        }

        Response:
        {
            "question": "What services does the company offer?",
            "answer": "Based on the website, the company offers...",
            "sources": [
                "https://tehisintellekt.ee/services",
                "https://tehisintellekt.ee/"
            ],
            "usage": {
                "input_tokens": 1250,
                "output_tokens": 87
            }
        }
    """
    return service.ask_question(request_data.question)
