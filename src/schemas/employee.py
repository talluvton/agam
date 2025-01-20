from pydantic import BaseModel, Field

class Employee(BaseModel):
    first_name: str = Field(min_length=2)
    last_name: str = Field(min_length=2)
    position: str = Field(min_length=2)
    government_id: int 
    employer_id: int = Field(default=None)


