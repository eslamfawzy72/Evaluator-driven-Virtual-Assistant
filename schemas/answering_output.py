from pydantic import BaseModel


class AnsweringResult(BaseModel):

    answer: str