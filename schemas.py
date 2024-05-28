from pydantic import BaseModel

class ZipFileMetadataBase(BaseModel):
    name: str
    path: str
    content_type: str
    size: int
    is_scanned: bool

class ZipFileMetadataCreate(ZipFileMetadataBase):
    pass

class ZipFileMetadata(ZipFileMetadataBase):
    id: int

    class Config:
        # orm_mode = True
        from_attributes = True


class AnalyzeRequest(BaseModel):
    file_id: int

class CodebaseBase(BaseModel):
    name: str
    description: str
    severity: str
    message: str
    path: str
    start_line: int
    start_column: int
    end_line: int
    end_column: int
    zipfilemetadata_id: int

class CodebaseCreate(CodebaseBase):
    pass

class Codebase(CodebaseBase):
    id: int

    class Config:
        # orm_mode = True
        from_attributes = True
        