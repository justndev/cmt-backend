from typing import Dict
import openai

from app.config import settings
from app.dtos.ask_response import AskResponse, AskFormat, Usage


class OpenAIService:
    """
    Requires OPENAI_API_KEY in .env
    """

    def __init__(self):
        """
        Initialize the OpenAI service with API credentials.

        Raises:
            Exception: If OPENAI_API_KEY is not set in environment variables
        """

        if not settings.OPENAI_API_KEY:
            raise Exception('OPENAI_API_KEY not set')

        openai.api_key = settings.OPENAI_API_KEY

    def answer_question(self, question: str, data: Dict[str, str]) -> AskResponse:
        """
        Generate an AI-powered answer to a question using provided context.

        Args:
            question (str): The user's question to be answered
            data (Dict[str, str]):
                Example: {"https://example.com": "Page content..."}

        Returns:
            AskResponse

        Raises:
            Exception: If the OpenAI API call fails
        """
        try:
            context = self._concatinate_content(data)

            system_rules = """
You are a helpful assistant.

Answer questions using only the information provided.

Always return valid JSON with 'answer' and 'sources'.
Answer in the language of question.
"""

            user_prompt = f"""Question: {question}

Information: {context}"""

            response = openai.responses.parse(
                model=settings.CHATGPT_MODEL,
                input=[
                    {"role": "system", "content": system_rules},
                    {"role": "user", "content": user_prompt},
                ],
                text_format=AskFormat,
            )

            structured_answer = response.output_parsed

            return AskResponse(
                question=structured_answer.question,
                answer=structured_answer.answer,
                sources=structured_answer.sources,
                usage=Usage(
                    input_tokens=response.usage.input_tokens,
                    output_tokens=response.usage.output_tokens
                )
            )

        except Exception as e:
            print(f"[OpenAIService] @answer_question: {e}")
            raise e

    def _concatinate_content(self, data: Dict[str, str]) -> str:
        return "\n\n".join([f"[{url}]\n{content}" for url, content in data.items()])
