from sqlmodel import create_engine, SQLModel

from app.models import models
from app.core.config import settings

engine = create_engine(settings.DATABASE_URI)

SQLModel.metadata.create_all(engine)
