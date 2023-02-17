from pathlib import Path
from typing import Iterator

import pytest
from flask import Flask
from todo_flask.todo.app import app, db


BASE_TEST_DIR = Path(__file__).parent


@pytest.fixture(scope="session")
def client():
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{BASE_TEST_DIR}/test.db"
    with app.app_context():
        db.init_app(app)
        db.create_all()
        yield app.test_client()
        db.drop_all()



#jak zaladowac dane do bazy danych przed testami
#todo ogarnac to wyzej