from sqlalchemy import Boolean, Column, ForeignKey, Integer, String

from database import Base  # it can be show error due to working directory


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String)


class Todos(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    priority = Column(Integer, index=True)
    completed = Column(Boolean, default=False, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

