# main.py
from fastapi import FastAPI, File, UploadFile, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import shutil
import os
from database import SessionLocal, engine
from models import Base, ZipFileMetadata
import schemas
import hashlib
import time
from typing import List
import random
import zipfile

# http://127.0.0.1:8000/docs
# http://127.0.0.1:8000/redoc

# - request codeql to scan this file
# - request llm to fix this file (vulnerability code)

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

    # save file
    if not os.path.exists("files"):
        os.makedirs("files")

    # create directory
    dirname = hashlib.md5(random.randbytes(32)).hexdigest() + \
        "-" + \
        str(int(time.time()))

    # make directory
    os.makedirs(f"files/{dirname}", exist_ok=True)

    # save file
    file_location = f"files/{dirname}/{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # check file size (100MB)
    if os.path.getsize(file_location) > 1024 * 1024:
        # remove file
        os.remove(file_location)
        raise HTTPException(status_code=400, detail="File size should be less than 1MB")

    # extract file
    try:
        with zipfile.ZipFile(file_location, 'r') as zip_ref:
            zip_ref.extractall(f"files/{dirname}")
    except Exception as e:
        raise HTTPException(status_code=400, detail="Failed to extract zip file")

        # remove zip file ?
        # os.remove(file_location)

    # save file metadata
    file_metadata = ZipFileMetadata(
        name=file.filename,
        path=f"files/{dirname}",
        content_type=file.content_type if file.content_type else "application/zip",
        size=os.path.getsize(file_location)
    )

    # save to db
    db.add(file_metadata)
    db.commit()
    db.refresh(file_metadata)

    return file_metadata

@app.get("/files/", response_model=List[schemas.ZipFileMetadata])
def read_files(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    files = db.query(ZipFileMetadata).offset(skip).limit(limit).all()
    return files




if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)