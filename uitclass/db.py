from contextlib import asynccontextmanager
from typing import Union, Optional, Annotated
#from fastapi_neon import settings
from sqlmodel import Field, Session, SQLModel, create_engine, select
from fastapi import FastAPI, Depends
from uitclass.conn_string import DATABASE_URL
import psycopg
import psycopg_binary


class Todo(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    text: str
    is_complete: bool = False

class TodoCreate(SQLModel):
    text:str
    is_complete:bool = False

class TodoRead(SQLModel):
    id: int
    text:str
    is_complete:bool

class TodoUpdate(SQLModel):
    id:int
    text: str
    is_complete: Optional[bool] = False

#print(DATABASE_URL)
connection_string = str(DATABASE_URL).replace(
    "postgresql", "postgresql+psycopg")
#print(connection_string)

# recycle connections after 5 minutes
# to correspond with the compute scale down
engine = create_engine(connection_string,echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
