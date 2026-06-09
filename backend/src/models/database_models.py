from sqlalchemy import Column, String, DateTime, func, JSON, Boolean
from sqlalchemy.dialects.postgresql import UUID
import uuid

from src.core.database import Base

class CoutureCollection(Base):
    __tablename__ = "couture_collections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trend_description = Column(String, nullable=False)
    monkey_tower_class = Column(String, nullable=False)
    collection_title = Column(String, nullable=False)
    species_fit = Column(String, nullable=False)
    keywords = Column(JSON, nullable=False)
    image_url = Column(String, nullable=False)
    fallback_used = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
