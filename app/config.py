import json
import os

CONFIG_FILE = 'proxmox_config.json'

def save_proxmox_config(host, user, password, login_method):
    if login_method == 'pam':
        user = f'{user}@pam'
    else:
        user = f'{user}@pve'
    config = {
        'host': host,
        'user': user,
        'password': password
    }
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)

def load_proxmox_config():
    if not os.path.exists(CONFIG_FILE):
        return None
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)
        