#initialize the db here 
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from config import settings

class Base(DeclarativeBase):
    pass

engine = create_engine(url=settings.database_url)
sessionLocal = sessionmaker(bind=engine)
#dependency to access the db inside the endpoints
def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()
