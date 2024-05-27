from pydantic import BaseModel

class ZipFileMetadataBase(BaseModel):
    file_name: str
    origin_name: str
    content_type: str
    size: int

class ZipFileMetadataCreate(ZipFileMetadataBase):
    pass

class ZipFileMetadata(ZipFileMetadataBase):
    id: int

    class Config:
        orm_mode = True
