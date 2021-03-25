from pymongo import MongoClient
from werkzeug.security import generate_password_hash
import os
from user import User

client = MongoClient(os.environ.get('MONGO_URL'))
chat_db = client.get_database('ChatApp')
user_collection = chat_db.get_collection('user')


def save_user(username, email, password, language):
    password_hash = generate_password_hash(password)
    user_collection.insert_one({'_id': username, 'email': email, 'password': password_hash, 'lang':language})


def get_user(username):
    user_data = user_collection.find_one({'_id': username})
    return User(user_data['_id'], user_data['email'], user_data['password'], user_data['lang']) if user_data else None
