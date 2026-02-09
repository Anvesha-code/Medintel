from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base import Base


class Chunk(Base):
    __tablename__ = "chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    user_id = Column(Integer, nullable=False)

    chunk_index = Column(Integer)
    chunk_text = Column(Text)
    source_type = Column(Text)

    # Optional relationship (safe)
    document = relationship("Document", backref="chunks")
