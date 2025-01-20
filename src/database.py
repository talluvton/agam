import psycopg2
from fastapi import HTTPException
import os
from dotenv import load_dotenv
import redis

load_dotenv()

class Database:
    def __init__(self, database_url, redis_url):
        self.conn = None
        self.database_url = database_url
        self.redis_client = redis.Redis.from_url(redis_url)

    def get_from_cache(self, key):
        return self.redis_client.get(key)

    def set_to_cache(self, key, value, expire=60):
        self.redis_client.set(key, value, ex=expire)

    def connect(self):
        try:
            self.conn = psycopg2.connect(self.database_url)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database connection error: {str(e)}")

    def execute_sql_file(self, file_path):
        try:
            with open(file_path, 'r') as file:
                sql_commands = file.read()

            with self.conn.cursor() as cursor:
                cursor.execute(sql_commands)
            self.commit()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error executing SQL file: {str(e)}")

    def load_employees(self, file_path):
        try:
            with self.conn.cursor() as cursor:
                cursor.callproc("is_table_empty", ("employees",))
                is_empty = cursor.fetchone()[0]
                if is_empty:
                    with open(file_path, 'r') as f:
                        next(f)  
                        with self.conn.cursor() as cursor:
                            cursor.copy_from(f, 'employees', sep=',', columns=('first_name', 'last_name', 'position', 'government_id'))
                    self.commit()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error loading employees table: {str(e)}")

    def load_employers(self, file_path):
        try:
            with self.conn.cursor() as cursor:
                cursor.callproc("is_table_empty", ("employers",))
                is_empty = cursor.fetchone()[0]
                if is_empty:
                    with open(file_path, 'r') as f:
                        with self.conn.cursor() as cursor:
                            cursor.copy_expert(
                                f"""COPY employers (employer_name, government_id) FROM STDIN WITH (FORMAT CSV, HEADER TRUE)""",
                                f
                            )
                    self.commit()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error loading employers table: {str(e)}")

    def commit(self):
        self.conn.commit()

    def close(self):
        if self.conn:
            self.conn.close()

db = Database(os.getenv("DATABASE_URL"), os.getenv("REDIS_URL"))