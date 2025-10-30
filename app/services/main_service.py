from fastapi import HTTPException

from app.db.database import SessionLocal
from app.services.page_crud import PageCrud
from app.services.openai_service import answer_question


class AppService:

    def __init__(self):
        self.page_crud = PageCrud(SessionLocal())

    def get_source(self):
        try:
            result = {}
            pages = self.page_crud.get_all_pages()

            for page in pages:
                result[page.url] = page.content
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def ask(self, question: str):
        try:
            data = ''
            pages = self.page_crud.get_all_pages()

            if not pages:
                raise HTTPException(status_code=500, detail='No information available')

            for page in pages:
                data += page.content
            return answer_question(question, data)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
