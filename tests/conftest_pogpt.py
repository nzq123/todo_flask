import pytest
from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from todo.app import app, db
from todo.app import Todo


SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        test_db = TestingSessionLocal()
        yield test_db
    finally:
        test_db.close()


@pytest.fixture()
def test_db():
    Todo.metadata.create_all(bind=engine)
    yield
    Todo.metadata.drop_all(bind=engine)

app.dependency_overrides[db] = override_get_db

client = Flask(app)


@pytest.fixture()
def client():
    return app.test_client()


@pytest.fixture(scope="function", autouse=True)
def function_test():
    print("FUNCTION FIXTURE")
    return


@pytest.fixture(scope="module", autouse=True)
def module_test():
    print("MODULE FIXTURE")
    return


@pytest.fixture(scope="session", autouse=True)
def session_test():
    print("SESSION FIXTURE")
    return


#TODO zobaczyc co to robi wyzej ok