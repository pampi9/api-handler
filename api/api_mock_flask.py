from flask import Flask
from flask import json
from flask_socketio import SocketIO

companies = [{"id": 1, "name": "Company One"}, {"id": 2, "name": "Company Two"}]

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socket_io = SocketIO(app)


@app.route('/v1', methods=['GET'])
def get_companies():
    return json.dumps(companies)


if __name__ == '__main__':
    socket_io.run(app, port=5005)
