# main.py 파일 내용
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to the HAT Project!"}

@app.get("/admin")
def read_admin():
    return {"page": "HAT Admin Panel", "status": "Ready"}