from sqlalchemy import  Column, Integer, String, Index
from sqlalchemy.orm import DeclarativeBase, relationship
import json
from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class Base(DeclarativeBase):
    pass 

class NameArchieve(Base):
    __tablename__ = 'names_archieve'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    country = Column(String, nullable=False)
    
    metaphones = relationship("Metaphone", back_populates="name")

class Metaphone(Base):
    __tablename__ = 'metaphones'
    
    # SQLAlchemy doesn't need a separate primary key column here
    name_id = Column(Integer, ForeignKey('names_archieve.id'), primary_key=True)
    metaphone = Column(String, nullable=False)
    
    name = relationship("NameArchieve", back_populates="metaphones")
    
    # Create the indexes
    __table_args__ = (
        Index('idx_metaphone', 'metaphone'),
    )

class InputNames(Base):
    __tablename__ = 'input_names'
    
    id = Column(Integer, primary_key=True)
    
    name = Column(String, nullable=False)
    country = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # One-to-many relationship with CorrectedNames
    corrected_names = relationship("CorrectedNames", back_populates="input_name")

class CorrectedNames(Base):
    __tablename__ = 'corrected_names'
    
    id = Column(Integer, primary_key=True)
    input_name_id = Column(Integer, ForeignKey('input_names.id'), nullable=False)
    
    suggested_name = Column(String, nullable=False)
    
    similarity_score = Column(Float, nullable=True)
    
    # Relationship back to InputNames
    input_name = relationship("InputNames", back_populates="corrected_names")
    
    __table_args__ = (
        Index('idx_input_name_id', 'input_name_id'),
        Index('idx_similarity_score', 'similarity_score'),
    )

