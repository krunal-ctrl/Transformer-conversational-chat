from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, join_room, leave_room
from googletrans import Translator
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from pymongo.errors import DuplicateKeyError

from database import get_user, save_user

app = Flask(__name__)
app.secret_key = "my_secret_key"
socketio = SocketIO(app, cors_allowed_origins="*")
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

clients = []
userdata = {}


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    message = ''
    if request.method == "POST":
        username = request.form.get('username')
        password_input = request.form.get('password')
        user = get_user(username)

        if user and user.check_password(password_input):
            login_user(user)
            return redirect(url_for('home'))
        else:
            message = 'Failed to login'
    return render_template('login.html', message=message)


@app.route("/signup", methods=["GET", "POST"])
def signup():

    if current_user.is_authenticated:
        return redirect(url_for('home'))

    message = ''
    if request.method == "POST":
        username = request.form.get('username')
        password_input = request.form.get('password')
        email = request.form.get('email')
        try:
            save_user(username, email, password_input)
            return redirect(url_for('login'))
        except DuplicateKeyError:
            message = "UserName already exists please try antoher name"
    return render_template('registration.html', message=message)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/chat')
@login_required
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


@login_manager.user_loader
def load_user(username):
    return get_user(username)


if __name__ == '__main__':
    socketio.run(app)
