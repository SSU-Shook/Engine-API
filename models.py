from sqlalchemy import Column, Integer, String
from database import Base

class ZipFileMetadata(Base):
    __tablename__ = "zipfile_metadata"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    path = Column(String)
    content_type = Column(String)
    size = Column(Integer)


# from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
# from sqlalchemy.orm import relationship

# from database import Base

# # Name | Description | Severity | Message | Path | Start line | End line | Start column | End line | End column

# class Codebase(Base):
#     __tablename__ = "codebases"

#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String, index=True)
#     description = Column(String, index=True)
#     severity = Column(String, index=True)
#     message = Column(String, index=True)
#     path = Column(String, index=True)
#     start_line = Column(Integer, index=True)
#     start_column = Column(Integer, index=True)
#     end_line = Column(Integer, index=True)
#     end_column = Column(Integer, index=True)