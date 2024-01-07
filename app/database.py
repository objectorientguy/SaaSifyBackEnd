from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "postgresql://postgres:Mun1chad$@localhost:5432/postgres"

# "postgresql://db_saasify_bb5z_user:SeyzkwBSm2YpekFp4VhHpqMaCYjTpVBX@dpg-cl6nv7oicrhc73fp5750-a.singapore-postgres.render.com/db_saasify_bb5z"


engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
