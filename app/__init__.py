from flask import Flask, redirect, url_for, flash, request
import os
import logging
from app.utils import connect_to_proxmox
from flask_wtf import CSRFProtect

proxmox = connect_to_proxmox()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your_secret_key_here'
    data_dir = './data'
    csrf = CSRFProtect(app)
    
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    app.config['JSON_FILE_PATH'] = os.path.join(data_dir, 'settings.json')

    with app.app_context():
        from . import routes

    @app.before_request
    def check_proxmox_connection():
        if proxmox is None and request.endpoint not in ['proxmox_config', 'login', 'register', 'static', 'favicon', 'hero']:
            flash('Proxmox configuration is not set up. Please configure it first.', 'warning')
            return redirect(url_for('proxmox_config'))
    
    return app