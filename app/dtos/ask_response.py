from pydantic import BaseModel

class Usage(BaseModel):
    input_tokens: int
    output_tokens: int

class AskFormat(BaseModel):
    question: str
    answer: str
    sources: list[str]

class AskResponse(AskFormat):
    usage: Usage


