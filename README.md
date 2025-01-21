# Agam Leaderim

Python FastAPI Project with Docker, PostgreSQL, Redis, Psycopg2, and Pydantic

## Requirements

Python >= 3.10
Docker
Docker Compose

## Instructions

I have included the default.env file in the repository.
Please note that you will need to create .env file according to the default.env file with the appropriate values.
Additionally, In the root of the project, create a folder named data.
Inside the data folder, place the required CSV files (employees.csv, employers.csv).

Use Docker Compose to build and run the application:

`docker-compose up --build`

## Access the app at:

http://127.0.0.1:8000/docs#/
