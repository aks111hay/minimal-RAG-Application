from pydantic import BaseModel

class DocumentInput(BaseModel):
    id : str
    text : str

class QueryInput(BaseModel):
    question : str