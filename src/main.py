from fastapi import FastAPI
from routers import employees, employers, auth
from database import db
import os

app = FastAPI()

@app.on_event("startup")
def startup():
    db.connect()
    db.execute_sql_file(os.getenv("DATABASE_SCHEMA_PATH"))
    db.load_employees(os.getenv("EMPLOYEES_FILE_PATH"))
    db.load_employers(os.getenv("EMPLOYERS_FILE_PATH"))

@app.on_event("shutdown")
def shutdown():
    db.close()

app.include_router(auth.router)
app.include_router(employees.router)
app.include_router(employers.router)


