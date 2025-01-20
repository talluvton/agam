from fastapi import HTTPException, Query, Depends
from database import db
from schemas.employer import Employer
from .auth import AuthClient
from typing import Annotated
import json

user_dependency = Annotated[dict, Depends(AuthClient.get_current_user)]

class EmployersClient():

    @classmethod
    def create_employer(cls, user: user_dependency, employer: Employer):
        try:
            if user is None:
                raise HTTPException(status_code=401, detail="Authentication failed.")
            created_by_user_id = user.get("id")
            employer_values = (*employer.dict().values(), created_by_user_id)
            with db.conn.cursor() as cursor:
                cursor.callproc("insert_employer", employer_values)
                db.commit()  
                return {"employer": employer, "message": "Employer created successfully"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error creating employer: {str(e)}")

    @classmethod
    def search_employers(cls, user: user_dependency, term: str, page_num: int = Query(1, ge=1), page_size: int = Query(10, ge=1)):
        try:
            if user is None:
                raise HTTPException(status_code=401, detail="Authentication failed.")
            cache_key = f"employers:{term}:{page_num}:{page_size}"
            cached_result = db.get_from_cache(cache_key)
            if cached_result:
                return json.loads(cached_result)
            with db.conn.cursor() as cursor:
                cursor.callproc("search_employers", (term, page_num, page_size))
                results = cursor.fetchall()
                total_count = results[0][-1] if results else 0  
                results = [result[:-2] for result in results]         
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error seach employers: {str(e)}")
        response = {
            "total": total_count,
            "page_num": page_num,
            "page_size": page_size,
            "data": results
        }
        db.set_to_cache(cache_key, json.dumps(response))
        return response