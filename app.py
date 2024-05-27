# main.py
from fastapi import FastAPI, File, UploadFile, Depends, HTTPException
from sqlalchemy.orm import Session
import shutil
import os
from database import SessionLocal, engine
from models import Base, ZipFileMetadata
import schemas
import hashlib
import time
from typing import List

# http://127.0.0.1:8000/docs
# http://127.0.0.1:8000/redoc

# - request codeql to scan this file
# - request llm to fix this file (vulnerability code)

Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/upload/", response_model=schemas.ZipFileMetadata)
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    # check extension
    if file.filename.split(".")[-1] not in ["zip"]:
        raise HTTPException(status_code=400, detail="Only zip files are allowed")

    # create unique name
    name = file.filename.split(".")[0] + "-" \
        + str(int(time.time())) + "-" + \
            hashlib.md5(str(int(time.time())).encode()).hexdigest() + "." + \
                file.filename.split(".")[-1]

    # save file
    if not os.path.exists("files"):
        os.makedirs("files")

    file_location = f"files/{name}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # save file metadata
    file_metadata = ZipFileMetadata(
        file_name=name,
        origin_name=file.filename,
        content_type=file.content_type,
        size=os.path.getsize(file_location)
    )

    # save to db
    db.add(file_metadata)
    db.commit()
    db.refresh(file_metadata)

    return file_metadata

@app.get("/files/", response_model=List[schemas.ZipFileMetadata])
def read_files(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    files = db.query(ZipFileMetadata).offset(skip).limit(limit).all()
    return files

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


# from fastapi import FastAPI, File, Form, UploadFile
# import models, crud, schemas
# from database import SessionLocal, engine, Base
# from sqlalchemy.orm import Session
# from fastapi import Depends, HTTPException, status
# from typing import List
# import shutil
# from schemas import ZipFile, ZipFileCreate
# import os
# # from models import Codebase, zipCodes


# ########### Todo ############

# # - redis cache

# Base.metadata.create_all(bind=engine)

# app = FastAPI()

# UPLOAD_FOLDER = "uploads"

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# @app.get("/")
# async def index():
#     return {"message": "Test"}

# # request codeql to scan this file
# # Codeql docker올려서 할라했는데 request보내서 할 수 있는 방법이 없어서 cli로 그냥 실행하도록 해야겠네요.
# # @app.post("/analyze")
# # async def analyze():
# #     return {"message": "Analyze"}

# # request llm to fix this file (vulnerability code)
# # @app.post("/fix")
# # async def fix():
# #     return {"message": "Fix"}

# # @app.get("/files/", response_model=list[ZipFile])
# # def read_files(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
# #     files = db.query(ZipFile).offset(skip).limit(limit).all()
# #     return files

# # @app.post("/upload/")
# # async def upload_file(
# #     file: UploadFile = File(...),
# #     description: str = Form(...)
# # ):
# #     return {
# #         "file_name": file.filename,
# #         "description": description,
# #         "content_type": file.content_type
# #     }

# # @app.post("/upload-multiple/")
# # async def upload_multiple_files(
# #     files: List[UploadFile] = File(...),
# #     descriptions: List[str] = Form(...)
# # ):
# #     return [
# #         {
# #             "file_name": file.filename,
# #             "description": description,
# #             "content_type": file.content_type
# #         }
# #         for file, description in zip(files, descriptions)
# #     ]