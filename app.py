# main.py
from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse
import shutil
import os
from database import SessionLocal, engine
from models import Base, ZipFileMetadata, Codebase
import schemas
import hashlib
import time
from typing import List
import random
import zipfile
import config
import subprocess
import csv
import sast_llm
from helper_utils import *
from patch_utils import *

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
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # process = subprocess.Popen(command, shell=True)
    return process

def add_codebase(db: Session, codebase_dict: dict) -> schemas.Codebase:
    db_codebase = Codebase(**codebase_dict)
    db.add(db_codebase)
    db.commit()
    db.refresh(db_codebase)
    return db_codebase

def do_patch(file_id):
    db = SessionLocal()
    file = db.query(ZipFileMetadata).filter(ZipFileMetadata.id == file_id).first()

    codebases = db.query(Codebase).filter(Codebase.zipfilemetadata_id == file_id).all()

    codeql_csv_path = f"results/{file.path}.csv"

    project_path = f'files/{file.path}'

    # patch_vulnerabilities(project_path, codeql_csv_path, code_style_profile=None, zero_shot_cot=False):
    # profile_assistant를 사용하여 코딩 컨벤션 프로파일링 결과를 얻는다. (json 문자열 형태)
    patched_vulnerabilities = sast_llm.patch_vulnerabilities(project_path, codeql_csv_path, code_style_profile=None, zero_shot_cot=False, rag=False)
    
    # print('[********]')
    # print(patched_vulnerabilities)
    # print('[********]')

    if len(patched_vulnerabilities['patched_files']) > 0:
        count = 1
        vuln_details = ""
        for original_path, patched_path in patched_vulnerabilities['patched_files'].items():
            with open(original_path, 'r') as f1:
                origin = f1.read()
                with open(patched_path, 'r') as f2:
                    patched = f2.read()
                    # diff = generate_diff(origin, patched) # helper_utils
                    diff = diff_code(origin, patched) # patch_utils
                    # print(diff)
            
            # patch description
            
            description = sast_llm.explain_patch(diff)

            patched_name = patched_vulnerabilities['vulnerabilities_by_file'][original_path]
            for vuln in patched_name:
                vuln_detail = config.VULN_DETAIL.format(idx=count,
                                                            vuln_name=vuln['name'],
                                                            path=vuln['path'],
                                                            severity=vuln['severity'],
                                                            description=vuln['description'],
                                                            message=vuln['message'],
                                                            original_code=origin,
                                                            patched_code=patched,
                                                            diff_code=diff,
                                                            patch_description=description)
                vuln_details += vuln_detail
                count += 1
    else:
        vuln_details = "No vulnerabilities are patched"
    
    # 리포트 markdown 템플릿 생성
    template = config.TEMPLATE.format(title=file.name,
                           date=time.strftime("%Y-%m-%d %H:%M:%S"),
                           model="GPT-4o",
                           vuln_count=len(codebases),
                            error_count=len([c for c in codebases if c.severity == "error"]),
                            warning_count=len([c for c in codebases if c.severity == "warning"]),
                            note_count=len([c for c in codebases if c.severity == "note"]),
                            details=vuln_details)
    
    os.makedirs("reports", exist_ok=True)

    with open(f"reports/{file.path}.md", 'w', encoding='utf-8') as f:
        print(f'writing report file: reports/{file.path}.md')
        f.write(template)
    
    # update db
    file.is_patched = True
    db.commit()
    # db.refresh(file)


    # return FileResponse(f"reports/{file.path}.md", media_type='application/octet-stream', filename=f"{file.path}.md", headers={"Content-Disposition": "attachment; filename=report.md"}, status_code=200)



@app.post("/upload/", response_model=schemas.ZipFileMetadata)
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    # check extension
    if file.filename.split(".")[-1] not in ["zip"]:
        raise HTTPException(status_code=400, detail="Only zip files are allowed")

    # save file
    # if not os.path.exists("files"):
    #     os.makedirs("files")
    os.makedirs("files", exist_ok=True)

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
    if os.path.getsize(file_location) > 1024 * 1024 * 100:
        # remove file
        os.remove(file_location)
        raise HTTPException(status_code=400, detail="File size should be less than 100MB")

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

@app.get("/file/{file_id}", response_model=schemas.ZipFileMetadata)
def read_file(file_id: int, db: Session = Depends(get_db)):
    file = db.query(ZipFileMetadata).filter(ZipFileMetadata.id == file_id).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    return file


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

    # if file is already scanned
    if file.is_scanned:
        codebases = db.query(Codebase).filter(Codebase.zipfilemetadata_id == file_id).all()
        return codebases

    os.makedirs("db", exist_ok=True)
    os.makedirs("results", exist_ok=True)

    command1 = config.CODEQL_CREATE_COMMAND.format(db_path = f"db/{file.path}",
                                                  src_path = f'files/{file.path}')
    # print(command1)

    try:
        p = execute_command(command1)
        # stdout1, stderr1 = p.wait()
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
        # stdout2, stderr2 = p.communicate()
        p.wait()
    except:
        raise HTTPException(status_code=500, detail="Failed to run codeql analysis")
    
    # update db
    file.is_scanned = True

    # print('finish')

    # parse result
    codebases = []
    try:
        with open(f"results/{file.path}.csv", 'r', encoding='utf-8') as f:
            rdr = csv.reader(f)
            if not rdr:
                return codebases
            for line in rdr:
                # update db
                codebase = Codebase(name=line[0], 
                                    description=line[1], 
                                    severity=line[2], 
                                    message=line[3], 
                                    path=line[4], 
                                    start_line=int(line[5]), 
                                    start_column=int(line[6]), 
                                    end_line=int(line[7]), 
                                    end_column=int(line[8]),
                                    zipfilemetadata_id=file_id)
                
                db.add(codebase)
                db.commit()
                db.refresh(codebase)

                codebases.append(codebase)
    except:
        raise HTTPException(status_code=500, detail="Failed to parse codeql analysis result")
    
    return codebases

@app.get("/patch/")
async def patch_file(background_tasks: BackgroundTasks, file_id: int = Query(..., description="ID of the file to patch"), db: Session = Depends(get_db)):
    # get file
    file = db.query(ZipFileMetadata).filter(ZipFileMetadata.id == file_id).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    # check file
    if not os.path.exists(f'files/{file.path}') or not os.path.isdir(f'files/{file.path}'):
        raise HTTPException(status_code=404, detail="File path not found")

    # check codebase
    codebases = db.query(Codebase).filter(Codebase.zipfilemetadata_id == file_id).all()
    if not codebases:
        raise HTTPException(status_code=404, detail="Codebases not found")
        # raise HTTPException(status_code=404, detail="Codebases not found")

    # check if patched
    # if all([c.is_patched for c in codebases]):
    #     return FileResponse(f"reports/{file.path}.md", media_type='application/octet-stream', filename=f"{file.path}.md", headers={"Content-Disposition": "attachment; filename=report.md"}, status_code=200)

    background_tasks.add_task(do_patch, file_id)

    return {"message": "Patching started"}
    # return {"message": "Patched successfully"}

@app.get("/download-report/")
async def download_report(file_id: int = Query(..., description="ID of the file to download report"), db: Session = Depends(get_db)):
    # get file
    file = db.query(ZipFileMetadata).filter(ZipFileMetadata.id == file_id).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    # not patched
    if not file.is_patched:
        raise HTTPException(status_code=400, detail="File is not patched yet")

    return FileResponse(f"reports/{file.path}.md", media_type='application/octet-stream', filename=f"{file.path}.md", headers={"Content-Disposition": "attachment; filename=report.md"}, status_code=200)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)