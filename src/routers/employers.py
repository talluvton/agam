from fastapi import APIRouter, Query, Depends 
from schemas.employer import Employer
from clients.employers import EmployersClient
from typing import Annotated
from clients.auth import AuthClient


user_dependency = Annotated[dict, Depends(AuthClient.get_current_user)]

router = APIRouter(prefix="/employers", tags=["Employers"])


@router.get("/search/")
def search_employers(user: user_dependency, term: str, page_num: int = Query(1, ge=1), page_size: int = Query(10, ge=1)):
    searched_employers = EmployersClient.search_employers(user, term, page_num, page_size)
    return searched_employers
  

@router.post("/create-employer/", status_code=201)
def create_employer(user: user_dependency, employer: Employer):
    return EmployersClient.create_employer(user, employer)




