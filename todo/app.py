import os
from flask import Flask, request, jsonify, Response, abort
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_migrate import Migrate
from sqlalchemy import MetaData
import enum
from functools import wraps


basedir = os.path.abspath(os.path.dirname(__file__))


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#https://stackoverflow.com/questions/45527323/flask-sqlalchemy-upgrade-failing-after-updating-models-need-an-explanation-on-h
naming_convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}
db = SQLAlchemy(metadata=MetaData(naming_convention=naming_convention))
db.init_app(app)


migrate = Migrate(app, db)
migrate.init_app(app, db, render_as_batch=True)


class TaskStatus(enum.Enum):
    TO_DO = 'to_do'
    IN_PROGRESS = 'in_progress'
    DONE = 'done'


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(30), nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    todos = db.relationship("Todo")


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    desc = db.Column(db.String(250), nullable=False)
    status = db.Column(db.Enum(TaskStatus), nullable=True, default=TaskStatus.TO_DO)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)


def require_user_id(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user_id = request.cookies.get('user_id')
        if not user_id:
            abort(403)
        user = User.query.filter(User.id == user_id).first()
        if not user:
            abort(403)
        return func(*args, **kwargs, user_id=user_id)
    return wrapper


def desc_validators(todo: str) -> list:
    tab = []
    if todo is None:
        tab.append({"message": "'desc' field cannot be Null"})
        return tab
    if not isinstance(todo, str):
        tab.append({"message": "'desc' field has to be string"})
    if len(str(todo)) <= 3:
        tab.append({"message": "'desc' field require minimum 4 characters"})
    return tab


@app.route('/get_cookie')
def get_cookie():
    name = request.cookies.get('user_id')
    return 'welcome ' + name


@app.route('/users')
def get_users() -> Response:
    tab = []
    users = User.query.all()
    for user in users:
        user_dict = {'user_id': user.id, 'login': user.login, 'password': user.password}
        tab.append(user_dict)
    return jsonify({'docs': tab, 'total': len(tab)})


@app.route('/users', methods=['POST'])
def create():
    login = request.json['login']
    password = request.json['password']
    new_user = User(login=login, password=password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"created": True})


@app.route('/login', methods=['POST'])
def login_method():
    login = request.json['login']
    user = User.query.filter(User.login == login).first()
    if user is None:
        return jsonify({"login": False})
    password = request.json['password']
    if user.password == password:
        out = jsonify(state=0, msg='success')
        out.set_cookie('user_id', str(user.id))
        return out
    return jsonify({"login": False})


@app.route('/logout', methods=['POST'])
def logout_method():
    out = jsonify(state=0, msg='success')
    out.delete_cookie('user_id')
    return out


@app.route('/todos')
@require_user_id
def get_todos(user_id) -> Response:
    tab = []
    todos = Todo.query.filter_by(user_id=user_id).all()
    for i in todos:
        date = str(i.date)
        todo_dict = {'id': i.id, 'date': date, 'desc': i.desc, 'user_id': i.user_id, 'status': i.status.value}
        tab.append(todo_dict)
    return jsonify({'docs': tab, 'total': len(tab)})


@app.route('/home/<int:todo_id>')
def show_todo(todo_id: int) -> tuple[Response, int]:
    todo = Todo.query.get(todo_id)
    if not todo:
        return jsonify({"message": f"No object with '{todo_id}' id"}), 404
    return jsonify({'id': todo.id, 'date': str(todo.date), 'desc': todo.desc}), 200


@app.route('/home', methods=['POST'])
@require_user_id
def create_todo(user_id) -> tuple[Response, int]:
    try:
        date = datetime.strptime(request.json['date'], '%Y-%m-%d %H:%M:%S.%f')
    except ValueError:
        return jsonify({'message': 'Invalid date format'}), 400
    except KeyError:
        return jsonify({"message": "'date' field is required"}), 400
    try:
        desc = request.json['desc']
    except KeyError:
        return jsonify({"message": "'desc' field is required"}), 400
    tab = desc_validators(desc)
    if len(tab) == 0:
        new_todo = Todo(date=date, desc=desc, user_id=user_id, status=TaskStatus.TO_DO)
        db.session.add(new_todo)
        db.session.commit()
        return jsonify({'message': 'New todo  was added ', 'id': new_todo.id}), 200
    else:
        return jsonify(tab), 400


@app.route('/home/<int:todo_id>', methods=['PUT'])
@require_user_id
def update_todo(todo_id: int, user_id) -> tuple[Response, int]:
    my_todo = Todo.query.get(todo_id)
    try:
        userid = int(user_id)
    except TypeError:
        return jsonify({"message": "TypeError "}), 401
    if my_todo.user_id != userid:
        return jsonify({"message": f"You are not allowed to edit this todo"}), 404
    if not my_todo:
        return jsonify({"message": f"No object with '{todo_id}' id"}), 404
    try:
        my_todo.date = datetime.strptime(request.json['date'], '%Y-%m-%d %H:%M:%S.%f')
        put_todo = request.json['desc']
        new_status_todo = request.json['status']
        new_status = TaskStatus[new_status_todo]
    except KeyError:
        return jsonify({"message": "KeyError"}), 400
    except ValueError:
        return jsonify({'message': 'Value Error '}), 400
    error_list = desc_validators(put_todo)
    if len(error_list) == 0:
        my_todo.desc = put_todo
        my_todo.status = new_status
        db.session.commit()
        return jsonify({"message": "Todo was updated", "id": todo_id}), 200
    else:
        return jsonify(error_list), 400


@app.route('/home/<int:todo_id>', methods=['DELETE'])
@require_user_id
def delete_todo(todo_id: int, user_id) -> tuple[Response, int]:
    del_todo = Todo.query.get(todo_id)
    if del_todo is None:
        return jsonify({'message': 'Error'}), 204
    if del_todo.user_id != user_id:
        return jsonify({"message": f"You are not allowed to delete this todo"}), 404
    db.session.delete(del_todo)
    db.session.commit()
    return jsonify({"message": "Todo was deleted", "id": todo_id}), 204


if __name__ == "__main__":
    with app.app_context():
        db.init_app(app)
        db.create_all()
    app.run(debug=True)



# TODO JAK NIE BEDZIE WIADOMO CO ZROBIC TO NP DODAC CZY COS ZOSTALO WYKONANE W ZADANIU
# opowiedziec o tym rawstringu jutro ok
# nauczyc sie roznic miedzy db.create_all(), db = SQLAlchemy(app), db.init_app(app)
# alembic_version trzyma obecną wersje migracji która bylą zaaplikowana na bazie
# czym jest migracja w bazach danych
# Object Relational Mapping, dzieki temu możesz korzystać z bazy danych jak byś korzystał z obiektów
# Odwzorowanie struktury zdefiniowanej w ORM w istniejacej bazie danych
# document.cookie = "user_id=cyferka"
# zaznaczanie done
# listowanie todo
