import os
import pytest
from sqlalchemy import create_engine
from todo.app import app, basedir, Todo, db
from flask_sqlalchemy import SQLAlchemy


@pytest.fixture(scope="session")
def connection(request):
    # Modify this URL according to your database backend
    engine = create_engine("sqlite:///test.db")

    with engine.connect() as connection:
        connection.execute(test_db)

    # Create a new engine/connection that will actually connect
    # to the test database we just created. This will be the
    # connection used by the test suite run.
    engine = create_engine(f"sqlite:/// + {os.path.join(basedir)}/{test_db}")
    connection = engine.connect()

    def teardown():
        connection.execute(test_db.drop.all())
        connection.close()

    request.addfinalizer(teardown)
    return connection


@pytest.fixture(scope="session", autouse=True)
def setup_db(connection, request):
    """Setup test database.

    Creates all database tables as declared in SQLAlchemy models,
    then proceeds to drop all the created tables after all tests
    have finished running.
    """
    Todo.metadata.bind = connection
    Todo.metadata.create_all()

    def teardown():
        Todo.metadata.drop_all()

    request.addfinalizer(teardown)


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