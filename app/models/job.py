from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Job(Base):
    __tablename__ = 'jobs'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    company = Column(String, index=True)
    location = Column(String)
    salary = Column(Float, nullable=True)
    created_at = Column(Integer)  # Timestamp for when the job was created
    updated_at = Column(Integer)  # Timestamp for when the job was last updated

    def __repr__(self):
        return f"<Job(title={self.title}, company={self.company}, location={self.location})>"