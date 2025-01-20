from fastapi import HTTPException, Query, Depends
from database import db
from schemas.employee import Employee
from typing import Annotated
from .auth import AuthClient
import json

user_dependency = Annotated[dict, Depends(AuthClient.get_current_user)]

class EmloyeesClient():

    @classmethod
    def create_employee(cls, user: user_dependency, employee: Employee):
        try:
            if user is None:
                raise HTTPException(status_code=401, detail="Authentication failed.")
            created_by_user_id = user.get("id")
            employee_values = (*employee.dict().values(), created_by_user_id)
            with db.conn.cursor() as cursor:
                cursor.callproc("insert_employee", employee_values)
                message = cursor.fetchone()[0]
                db.commit()  
            return {"employee": employee, "message": message}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error creating employee: {str(e)}")

    @classmethod
    def search_employees(cls, user: user_dependency, term: str, page_num: int = Query(1, ge=1), page_size: int = Query(10, ge=1)):
        try:
            if user is None:
                raise HTTPException(status_code=401, detail="Authentication failed.")
            cache_key = f"employees:{term}:{page_num}:{page_size}"
            cached_result = db.get_from_cache(cache_key)
            if cached_result:
                return json.loads(cached_result)
            with db.conn.cursor() as cursor:
                cursor.callproc("search_employees", (term, page_num, page_size))
                results = cursor.fetchall()
                total_count = results[0][-1] if results else 0  
                results = [result[:-2] for result in results]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error searching employees: {str(e)}")
        response = {
            "total": total_count,
            "page_num": page_num,
            "page_size": page_size,
            "data": results,
        }
        db.set_to_cache(cache_key, json.dumps(response))
        return response
    
    @classmethod
    def attach_employee_to_employer(cls, user: user_dependency, employee_id: int = Query(1, ge=1), employer_id: int = Query(2, ge=1)):
        try:
            if user is None:
                raise HTTPException(status_code=401, detail="Authentication failed.")
            with db.conn.cursor() as cursor:
                cursor.callproc("attach_employee_to_employer", (employee_id, employer_id))
                message = cursor.fetchone()[0]
                db.commit()  
            return {"message": message}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error attaching employee: {str(e)}")