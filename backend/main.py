from fastapi import FastAPI
from sqlalchemy import text

from app.database import engine

app = FastAPI()


@app.get("/db-test")
def db_test():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"status": "database connection ok"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}
