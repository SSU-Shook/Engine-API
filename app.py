# main.py
from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, Query
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
import config
import subprocess
import csv

# http://127.0.0.1:8000/docs
# http://127.0.0.1:8000/redoc

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

def execute_command(command):
    process = subprocess.Popen(command, shell=True)
    return process

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
            # remove zip file ?
            # os.remove(file_location)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Failed to extract zip file")

    # save file metadata
    file_metadata = ZipFileMetadata(
        name=file.filename,
        path=dirname,
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


# codeql analysis
@app.get("/analyze/", response_model=List[schemas.Codebase])
async def analyze_file(file_id: int = Query(..., description="ID of the file to analyze"), db: Session = Depends(get_db)):
    # get file
    file = db.query(ZipFileMetadata).filter(ZipFileMetadata.id == file_id).first()
    # print(file)
    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    # check file
    if not os.path.exists(f'files/{file.path}') or not os.path.isdir(f'files/{file.path}'):
        raise HTTPException(status_code=404, detail="File path not found")

    os.makedirs("db", exist_ok=True)
    os.makedirs("results", exist_ok=True)

    command1 = config.CODEQL_CREATE_COMMAND.format(db_path = f"db/{file.path}",
                                                  src_path = f'files/{file.path}')
    # print(command1)

    try:
        p = execute_command(command1)
        p.wait()
    except:
        raise HTTPException(status_code=500, detail="Failed to create codeql database")

    # run codeql analysis
    command2 = config.CODEQL_ANALYSIS_COMMAND.format(db_path = f"db/{file.path}",
                                                     ql_path = config.CODEQL_QL_PATH,
                                                     output_path = f"results/{file.path}.csv",)
    # print(command2)
    try:
        p = execute_command(command2)
        p.wait()
    except:
        raise HTTPException(status_code=500, detail="Failed to run codeql analysis")
    
    # update db
    file.analyzed = True

    # parse result
    codebases = []
    try:
        with open(f"results/{file.path}.csv", 'r', encoding='utf-8') as f:
            rdr = csv.reader(f)
            for line in rdr:
                # update db
                codebase = schemas.Codebase(name=line[0], description=line[1], severity=line[2], message=line[3], path=line[4], start_line=int(line[5]), start_column=int(line[6]), end_line=int(line[7]), end_column=int(line[8]), zipfilemetadata_id=file_id)
                codebases.append(codebase)
    except:
        raise HTTPException(status_code=500, detail="Failed to parse codeql analysis result")

    return codebases

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001)