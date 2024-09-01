from flask import Flask
import os
import logging


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your_secret_key_here'
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    data_dir = './data'
    
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    app.config['JSON_FILE_PATH'] = os.path.join(data_dir, 'settings.json')

    with app.app_context():
        from . import routes
    
    return app