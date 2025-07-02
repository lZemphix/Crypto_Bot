from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .config import settings

engine = create_engine(url=settings.db_url)
sync_session = sessionmaker(engine)
