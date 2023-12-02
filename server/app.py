from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages/<int:id>', methods=['PATCH', 'DELETE'])
def messages_by_id(id):
    message = Message.query.filter_by(id=id).first()
    if request.method == 'PATCH':
        for attribute in request.json:
            setattr(message, attribute, request.json.get(attribute))
        db.session.commit()
        message_to_dict = message.to_dict() 
        response = jsonify(message_to_dict)
        response_body = make_response(response, 200)
        response_body.headers["Content-Type"] = "application/json"
        return response_body
    elif request.method == "DELETE":
        db.session.delete(message)
        db.session.commit()
        response_body = {'message': 'Delete was successful'}
        response = make_response(jsonify(response_body), 200)
        response.headers["Content-Type"] = "application/json"
        return response

@app.route('/messages', methods=['GET', 'POST'])
def get_messages():
    if request.method == 'GET':
        messages = Message.query.order_by(Message.created_at.asc()).all()
        messages_list = [{'id': msg.id, 'body': msg.body, 'created_at': msg.created_at, 'updated_at': msg.updated_at} for msg in messages]
        response = jsonify(messages_list)
        return make_response(response, 200)
    elif request.method == 'POST':
        new_message = Message(
            body=request.json.get("body"),
            username=request.json.get("username"),
            created_at=request.json.get("created_at"),
            updated_at=request.json.get("updated_at")
        )
        db.session.add(new_message)
        db.session.commit()
        new_message_to_dict = new_message.to_dict()
        response = jsonify(new_message_to_dict)
        return make_response(response, 200)

if __name__ == '__main__':
    app.run(port=5555)
