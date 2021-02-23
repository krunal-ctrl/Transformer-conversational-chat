from pymongo import MongoClient
from werkzeug.security import generate_password_hash
import api
client = MongoClient(api.API)

chat_db = client.get_database('ChatApp')
user_collection = chat_db.get_collection('user')


def save_user(username, email, password):
    password_hash = generate_password_hash(password)
    user_collection.insert_one({'_id': username, 'email': email, 'password': password_hash})