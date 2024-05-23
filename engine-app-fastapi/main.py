from fastapi import FastAPI, File, Form, UploadFile
import models, crud, schemas
from database import SessionLocal, engine
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from typing import List


# http://127.0.0.1:8000/docs
# http://127.0.0.1:8000/redoc

########### Todo ############
# - request codeql to scan this file
# - request llm to fix this file (vulnerability code)
# - redis cache

app = FastAPI()

@app.get("/")
async def index():
    return {"message": "Hello World"}

# request codeql to scan this file
# Codeql docker올려서 할라했는데 request보내서 할 수 있는 방법이 없어서 cli로 그냥 실행하도록 해야겠네요.
@app.post("/analyze")
async def analyze():
    return {"message": "Analyze"}

# request llm to fix this file (vulnerability code)
@app.post("/fix")
async def fix():
    return {"message": "Fix"}

@app.post("/upload/")
async def upload_file(
    file: UploadFile = File(...),
    description: str = Form(...)
):
    return {
        "file_name": file.filename,
        "description": description,
        "content_type": file.content_type
    }

@app.post("/upload-multiple/")
async def upload_multiple_files(
    files: List[UploadFile] = File(...),
    descriptions: List[str] = Form(...)
):
    return [
        {
            "file_name": file.filename,
            "description": description,
            "content_type": file.content_type
        }
        for file, description in zip(files, descriptions)
    ]