import bcrypt
import json
import os
from flask import current_app as app

USER_FILE = app.config['JSON_FILE_PATH']

# Function to encrypt a password
def encrypt_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password

# Function to check if a password matches the encrypted password
def check_password(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password)

# Function to save user data to a file
def save_user(username, password):
    hashed_password = encrypt_password(password)
    user_data = {
        'username': username,
        'password': hashed_password.decode('utf-8')
    }
    with open(USER_FILE, 'w') as f:
        json.dump(user_data, f)

# Function to load user data from a file
def load_user():
    if not os.path.exists(USER_FILE):
        return None
    with open(USER_FILE, 'r') as f:
        user_data = json.load(f)
    user_data['password'] = user_data['password'].encode('utf-8')
    return user_data

# Function to authenticate user
def authenticate(username, password):
    user_data = load_user()
    if user_data and user_data['username'] == username:
        return check_password(password, user_data['password'])
    return False