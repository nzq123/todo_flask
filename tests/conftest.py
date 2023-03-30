from pathlib import Path
from datetime import datetime
import pytest
from todo.app import app, db, Todo


BASE_TEST_DIR = Path(__file__).parent


@pytest.fixture(scope="session")
def client():
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{BASE_TEST_DIR}/test.db"
    with app.app_context():
        db.init_app(app)
        db.create_all()
        todo = Todo(date=datetime(year=2001, month=9, day=11), desc="abc")
        db.session.add(todo)
        db.session.commit()
        yield app.test_client()
        db.drop_all()

