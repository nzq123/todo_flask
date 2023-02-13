import os
from flask import Flask, render_template, request, url_for, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
import json
from datetime import datetime

from sqlalchemy.sql import func

basedir = os.path.abspath(os.path.dirname(__file__))


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
db.init_app(app)


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    desc = db.Column(db.String(100), nullable=False)


@app.route('/home')
def get_todos():
    tab = []
    todos = Todo.query.all()
    for i in todos:
        date = str(i.date)
        todo_dict = {'id': i.id, 'date': date, 'desc': i.desc}
        tab.append(todo_dict)
    return jsonify({'docs': tab, 'total': len(tab)})


@app.route('/home/<int:todo_id>')
def show_todo(todo_id):
    todo = Todo.query.get(todo_id)
    if not todo:
        return jsonify({"message": "Error", "No object with id": todo_id}), 404
    return jsonify({'id': todo.id, 'date': todo.date, 'desc': todo.desc}), 200


@app.route('/home', methods=['POST'])
def create_todo():
    try:
        date = datetime.strptime(request.json['date'], '%Y-%m-%d %H:%M:%S.%f')
    except ValueError: #TODO  zwracac dobry blad z expection
        return jsonify({'message': 'Value Error '}), 400
    desc = request.json['desc']
    if date is None or desc is None:
        return jsonify({"message": "Error"}), 400
    new_todo = Todo(date=date, desc=desc)
    db.session.add(new_todo)
    db.session.commit()
    return jsonify({'message': 'New todo  was added ', 'id': new_todo.id}), 200


@app.route('/home/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    upd_todo = Todo.query.get(todo_id)
    if not upd_todo:
        return jsonify({"message": "Error", "No object with id": todo_id}), 404
    try:
        upd_todo.date = datetime.strptime(request.json['date'], '%Y-%m-%d %H:%M:%S.%f')
    except ValueError: #TODO  zwracac dobry blad z expection
        return jsonify({'message': 'Value Error '}), 400
    upd_todo.desc = request.json['desc']
    db.session.commit()
    return jsonify({"message": "Todo was updated", "id": todo_id}), 200


@app.route('/home/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    del_todo = Todo.query.get(todo_id)
    if del_todo is None:
        return jsonify({'message': 'Error'}), 404
    db.session.delete(del_todo)
    db.session.commit()
    return jsonify({"message": "Todo was deleted", "id": todo_id}), 200


with app.app_context():
    db.create_all()


if __name__=="__main__":
    app.run(debug=True)

#TODO  zwracac dobry blad z expection