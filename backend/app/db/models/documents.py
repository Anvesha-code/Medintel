from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

from app.db.base import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)

    filename = Column(String, nullable=False)
    file_type = Column(String)

    upload_time = Column(DateTime, default=datetime.utcnow)

    user_id = Column(Integer, index=True)

    page_count = Column(Integer)
    sheet_count = Column(Integer)

    language = Column(String)
    extraction_status = Column(String)
