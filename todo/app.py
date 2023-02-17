import os
from flask import Flask, render_template, request, url_for, redirect, jsonify, Response, Request
from flask_sqlalchemy import SQLAlchemy
import json
from datetime import datetime

from sqlalchemy.sql import func

basedir = os.path.abspath(os.path.dirname(__file__))


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy()


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    desc = db.Column(db.String(250), nullable=False)


@app.route('/home')
def get_todos() -> Response:
    tab = []
    todos = Todo.query.all()
    for i in todos:
        date = str(i.date)
        todo_dict = {'id': i.id, 'date': date, 'desc': i.desc}
        tab.append(todo_dict)
    return jsonify({'docs': tab, 'total': len(tab)})


@app.route('/home/<int:todo_id>')
def show_todo(todo_id: int) -> tuple[Response, int]:
    todo = Todo.query.get(todo_id)
    if not todo:
        return jsonify({"message": f"No object with '{todo_id}' id"}), 404
    return jsonify({'id': todo.id, 'date': todo.date, 'desc': todo.desc}), 200


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


@app.route('/home', methods=['POST'])
def create_todo() -> tuple[Response, int]:
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
        new_todo = Todo(date=date, desc=desc)
        db.session.add(new_todo)
        db.session.commit()
        return jsonify({'message': 'New todo  was added ', 'id': new_todo.id}), 200
    else:
        return jsonify(tab), 400


@app.route('/home/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id: int) -> tuple[Response, int]:
    upd_todo = Todo.query.get(todo_id)
    if not upd_todo:
        return jsonify({"message": f"No object with '{todo_id}' id"}), 404
    try:
        upd_todo.date = datetime.strptime(request.json['date'], '%Y-%m-%d %H:%M:%S.%f')
    except ValueError:
        return jsonify({'message': 'Value Error '}), 400
    try:
        put_todo = request.json['desc']
    except KeyError:
        return jsonify({"message": "'desc' field is required"}), 400
    tab = desc_validators(put_todo)
    if len(tab) == 0:
        upd_todo.desc = put_todo
        db.session.commit()
        return jsonify({"message": "Todo was updated", "id": todo_id}), 200
    else:
        return jsonify(tab), 400


@app.route('/home/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id: int) -> tuple[Response, int]:
    del_todo = Todo.query.get(todo_id)
    if del_todo is None:
        return jsonify({'message': 'Error'}), 404
    db.session.delete(del_todo)
    db.session.commit()
    return jsonify({"message": "Todo was deleted", "id": todo_id}), 200


if __name__=="__main__":
    with app.app_context():
        db.init_app(app)
        db.create_all()
    app.run(debug=True)



#TODO JAK NIE BEDZIE WIADOMO CO ZROBIC TO NP DODAC CZY COS ZOSTALO WYKONANE W ZADANIU
# opowiedziec o tym rawstringu jutro ok
#nauczyc sie roznic miedzy db.create_all(), db = SQLAlchemy(app), db.init_app(app)