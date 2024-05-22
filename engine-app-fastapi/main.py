from fastapi import FastAPI
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