from pydantic import BaseModel,Field
from typing import List

class SubQuery(BaseModel):
    text : str = Field(description="The atomic subquery")

class QueryBatch(BaseModel):
    categories : List[List[SubQuery]]= Field(
        description="Nested groupings of queries broken down by intent categories."
    )


class QueryInputPayload(BaseModel):
    original_query : str
    structured_batch : QueryBatch
    