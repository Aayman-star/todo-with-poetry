# fastapi_neon/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI,Body,Depends,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, delete,select
from uitclass.db import Todo, TodoCreate,TodoRead,TodoUpdate,create_db_and_tables,engine
from typing import List,Annotated

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Creating tables..")
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan,title="Todo App with FastAPI", 
    version="0.0.1",
    servers=[
        {
            "url": "http://127.0.0.1:8000", # ADD NGROK URL Here Before Creating GPT Action
            "description": "Development Server"
        }
        ])
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Dependency
def get_session():
    with Session(engine) as session:
        yield session


@app.get("/",response_model=List[TodoRead])
def read_todos(*,session: Annotated[Session, Depends(get_session)]):
    """Get all Todos"""
    todos = session.exec(select(Todo).order_by(Todo.id)).all()
    if not todos:
        raise HTTPException(status_code=404, detail="No todos found")
    return todos


@app.post("/create-todo",response_model=TodoRead)
def create_todo(*,session: Annotated[Session, Depends(get_session)],todo:TodoCreate):
    """Creating and storing a todo item in the database"""
    todo_item = Todo.model_validate(todo)
    session.add(todo_item)
    session.commit()
    session.refresh(todo_item)
    return todo_item

@app.get("/complete-todos",response_model=List[TodoRead])
def get_complete_todos(*,session: Annotated[Session, Depends(get_session)]):
    """Get all complete todos"""
    todos = session.exec(select(Todo).where(Todo.is_complete == True)).all()
    if not todos:
        raise HTTPException(status_code=404, detail="No todos found")
    return todos

@app.get("/incomplete-todos",response_model=List[TodoRead])
def get_complete_todos(*,session: Annotated[Session, Depends(get_session)]):
    """Get all complete todos"""
    todos = session.exec(select(Todo).where(Todo.is_complete == False)).all()
    if not todos:
        raise HTTPException(status_code=404, detail="No todos found")
    return todos

@app.put("/check-todo/{task_id}")
def check_task(*,session: Annotated[Session, Depends(get_session)],task_id:int):
    """Check a task as complete"""
    db_todo = session.get(Todo, task_id)  # Get the todo item from the database
    if not db_todo :
        raise HTTPException(status_code=404, detail="Todo not found")
    db_todo.is_complete = not db_todo.is_complete
    session.add(db_todo)  # Add the updated todo to the session
    session.commit()
    session.refresh(db_todo)
    return db_todo

@app.put("/update-todo/{task_id}",response_model=TodoRead)
def update_todo(*,session: Annotated[Session, Depends(get_session)],task_id:int,todo:TodoUpdate):
    print(task_id,todo)
    """Update Todo Description"""
    db_todo = session.get(Todo,task_id)
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    todo_data = todo.model_dump(exclude_unset=True)
    print(todo_data)
    for key, value in todo_data.items():
        setattr(db_todo, key, value)
    print(db_todo)
    session.add(db_todo)  # Add the updated todo to the session 
    session.commit()
    session.refresh(db_todo)
    return db_todo

@app.delete("/del/{todo_id}")
def delete_todo(*,session: Annotated[Session, Depends(get_session)],todo_id:int):
    """Delete a todo from the database"""
    print(f"This is the id {todo_id}")
    todo = session.get(Todo,todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    session.delete(todo)
    session.commit()
    return {"message": "Todo deleted successfully"}

@app.delete("/delete-all")
def delete_all(*,session: Annotated[Session, Depends(get_session)]):
    """Delete all todos from the database"""
    result = session.exec(delete(Todo))
    session.commit()
    return {"message": f"{result.rowcount} todos deleted successfully"}



