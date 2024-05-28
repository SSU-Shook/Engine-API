from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import Boolean
from database import Base

class ZipFileMetadata(Base):
    __tablename__ = "zipfile_metadata"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    path = Column(String)
    content_type = Column(String)
    size = Column(Integer)
    is_scanned = Column(Boolean, default=False)

    # Relationship to Codebase
    codebases = relationship("Codebase", back_populates="zipfilemetadata")

class Codebase(Base):
    __tablename__ = "codebases"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, index=True)
    severity = Column(String, index=True)
    message = Column(String, index=True)
    path = Column(String, index=True)
    start_line = Column(Integer, index=True)
    start_column = Column(Integer, index=True)
    end_line = Column(Integer, index=True)
    end_column = Column(Integer, index=True)
    zipfilemetadata_id = Column(Integer, ForeignKey("zipfile_metadata.id"))

    # Relationship to ZipFileMetadata
    zipfilemetadata = relationship("ZipFileMetadata", back_populates="codebases")
