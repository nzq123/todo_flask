import pytest
from todo.app import app


@pytest.fixture()
def client():
    return app.test_client()


#TODO zobaczyc co to robi wyzej ok