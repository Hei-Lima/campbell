from flask import render_template, current_app as app
from app.utils import connect_to_proxmox, list_vms

proxmox = connect_to_proxmox()

@app.route('/')
def index():
    vms = list_vms()
    print(vms)
    return render_template('index.html', vms=vms)

@app.route('/login')
def login():
    return render_template('login.html')
