from fastapi import APIRouter, Query, Depends
from schemas.employee import Employee
from clients.employees import EmloyeesClient
from clients.auth import AuthClient
from typing import Annotated

router = APIRouter(prefix="/employees", tags=["Employees"])

user_dependency = Annotated[dict, Depends(AuthClient.get_current_user)]

@router.get("/search/")
async def search_employees(user: user_dependency, term: str, page_num: int = Query(1, ge=1), page_size: int = Query(10, ge=1)):
    return EmloyeesClient.search_employees(user, term, page_num, page_size)


@router.post("/create-employee/", status_code=201)
async def create_employee(user: user_dependency, employee: Employee):
    return EmloyeesClient.create_employee(user, employee)


@router.put("/{employee_id}/attach-employee-to-employer/", status_code=200)
async def attach_employee_to_employer(user: user_dependency, employee_id: int, employer_id: int):
    return EmloyeesClient.attach_employee_to_employer(user, employee_id, employer_id)