from pydantic import BaseModel

class ZipFileMetadataBase(BaseModel):
    name: str
    path: str
    content_type: str
    size: int

class ZipFileMetadataCreate(ZipFileMetadataBase):
    pass

class ZipFileMetadata(ZipFileMetadataBase):
    id: int

    class Config:
        # orm_mode = True
        from_attributes = True
