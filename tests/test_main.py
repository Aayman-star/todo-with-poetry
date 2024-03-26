import pytest
from fastapi import FastAPI,HTTPException
from fastapi.testclient import TestClient
from sqlmodel import Session,Field,SQLModel,create_engine,select
from uitclass.main import app,get_session
from uitclass.db import TodoCreate,TodoRead,TodoUpdate,Todo
from uitclass.conn_string import TEST_DATABASE_URL


@pytest.fixture(name="session")
def session_fixture():
    connection_string = str(TEST_DATABASE_URL).replace(
    "postgresql", "postgresql+psycopg")
    engine = create_engine(
        connection_string, 
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app=app) 
    yield client
    app.dependency_overrides.clear()


"""Test to create a todo"""
def test_create_todo(session:Session ,client: TestClient):
    response = client.post(
        "/create-todo", json={"text": "test todo", "is_complete":False}
    )
    data = response.json()

    assert response.status_code == 200
    assert data["text"] == "test todo"
    assert data["is_complete"] == False
    assert data["id"] is not None

"""Test to read a todo"""	
def test_read_todos(session:Session,client: TestClient):
  response = client.get("/")
  assert response.status_code == 200
  



"""Test to get the list of complete todos"""
def test_get_complete_todos(session:Session,client:TestClient):
    todo = Todo(text="test todo", is_complete=True)
    session.add(todo)
    session.commit()
    #session.refresh(todo)
    # Assuming there are complete todos in the database
    response = client.get("/complete-todos")
    data = response.json()
   
    assert response.status_code == 200
    assert data[0]["is_complete"] == todo.is_complete
    


"""test to get the list of incomplete todos"""
def test_get_incomplete_todos(session:Session,client:TestClient):
    todo = Todo(text="test todo", is_complete=False)
    session.add(todo)
    session.commit()
    #session.refresh(todo)
    # Assuming there are complete todos in the database
    response = client.get("/incomplete-todos")
    data = response.json()
   
    assert response.status_code == 200
   
    assert data[0]["is_complete"] == todo.is_complete


"""Test to update the text of the todo"""
def test_update_todo(session:Session, client:TestClient):
    todo = Todo(text="test todo", is_complete=False)
    session.add(todo)
    session.commit()
   
    response = client.put(f"/update-todo/{todo.id}",json={"id": todo.id,"text": "updated todo"})
    data = response.json()

    assert response.status_code == 200
    assert data["id"] == todo.id
    assert data["text"] == "updated todo"
    

""""Test to check the todo"""
def test_check_todo(session:Session, client:TestClient):
    todo = Todo(text="test todo", is_complete=False)
    session.add(todo)
    session.commit()

    response = client.put(f"/check-todo/{todo.id}")
    data = response.json()

    assert response.status_code == 200
    assert data["id"] == todo.id
    assert data["is_complete"] == True


"""Test to delete the todo"""
def test_delete_todo(session: Session, client: TestClient):
    todo = Todo(text="test todo", is_complete=False)
    session.add(todo)
    session.commit()

    response = client.delete(f"/del/{todo.id}")
    todo_in_db = session.get(Todo, todo.id)
    assert response.status_code == 200
    assert todo_in_db is None
