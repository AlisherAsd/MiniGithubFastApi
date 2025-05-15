from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    login = Column(String, unique=True, index=True)
    password = Column(String)
    email = Column(String, unique=True, index=True)
    isAuth = Column(Boolean, default=False)

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    files = relationship("File", back_populates="project")

class File(Base):
    __tablename__ = "files"
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String)
    name = Column(String)
    project_id = Column(Integer, ForeignKey("projects.id"))
    project = relationship("Project", back_populates="files")
