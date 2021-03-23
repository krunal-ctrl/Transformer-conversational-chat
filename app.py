from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, join_room, leave_room
from googletrans import Translator

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
clients = []
userdata = {}


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/chat')
def chat():
    username = request.args.get('username')
    room = request.args.get('room')
    lang = request.args.get('lang')

    if username and room:
        return render_template('chat.html', username=username, room=room, lang=lang)
    else:
        return redirect(url_for('home'))


@socketio.on('send_message')
def handle_send_message_event(data):
    app.logger.info("{} has sent message to the room {}: {} in {}".format(data['username'],
                                                                          data['room'],
                                                                          data['message'], data['lang']))
    for sid in clients:
        # print(userdata[sid], data['lang'])
        translator = Translator()
        data['message'] = str(translator.translate(data['message'], dest=userdata[sid]).text)
        socketio.emit('receive_message', data, room=sid)


@socketio.on('join_room')
def handle_join_room_event(data):
    app.logger.info("{} has joined the room {}".format(data['username'], data['room']))
    print(data)
    join_room(data['room'])
    clients.append(request.sid)  # collect sid so we can use it for later use
    userdata[request.sid] = data['lang']
    socketio.emit('join_room_announcement', data, room=data['room'])


@socketio.on('leave_room')
def handle_leave_room_event(data):
    app.logger.info("{} has left the room {}".format(data['username'], data['room']))
    leave_room(data['room'])
    socketio.emit('leave_room_announcement', data, room=data['room'])


if __name__ == '__main__':
    socketio.run(app)
