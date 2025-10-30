from sqlmodel import SQLModel
from app.db.session import engine
from app.models.user_model import User

def init_db():
    print("Creating database tables....")
    SQLModel.metadata.create_all(bind=engine)
    print("Tables created Successfully.")