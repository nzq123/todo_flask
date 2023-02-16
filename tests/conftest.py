import json
from pathlib import Path
from typing import Iterator

import pytest
from flask import Flask
from flask.testing import FlaskClient
from flask_sqlalchemy import SQLAlchemy

from todo.app import Todo, app, db

BASE_TEST_DIR = Path(__file__).parent


@pytest.fixture(scope="session")
def db_path() -> Iterator[str]:
    """
    Create test databse in tests folder.
    Remove after.
    """
    path = BASE_TEST_DIR / "test.db"
    path.touch(exist_ok=True)
    yield str(path)
    path.unlink()


@pytest.fixture(scope="session")
def test_app(db_path: str) -> Iterator[Flask]:
    # Overwrite application settings to use test database
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"

    # This is a hack to make it work and avoid ugly exception:
    #       https://stackoverflow.com/questions/24877025/runtimeerror-working-outside-of-application-context-when-unit-testing-with-py
    ctx = app.app_context()
    ctx.push()
    yield app
    ctx.pop()


@pytest.fixture(scope="session")
def test_db(test_app: Flask) -> SQLAlchemy:
    db.init_app(test_app)
    db.create_all()
    print(f'{test_app.config} TUTAJ JESTEM!!!!!!!!!!!!!!!!!!!!!!!!!')
    new_todo = Todo(date="2023-02-11 18:03:56.028704", desc='6565')
    db.session.add(new_todo)
    db.session.commit()
    return db


@pytest.fixture(scope="session")
def client(test_app: Flask) -> FlaskClient:
    return test_app.test_client()





#jak zaladowac dane do bazy danych przed testami
#todo ogarnac to wyzej