from pydantic import BaseModel, Field

class Employer(BaseModel):
    employer_name: str = Field(min_length=2)
    government_id: int = Field(ge=1)
