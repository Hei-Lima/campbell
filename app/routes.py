from flask import render_template, url_for, request, jsonify, current_app as app
from app.utils import *

proxmox = connect_to_proxmox()

@app.route('/')
def index():
    vms = list_vms(proxmox)
    print(vms)
    return render_template('index.html', vms=vms)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/create')
def create():
    nodes = list_nodes(proxmox)
    return render_template('create.html', nodes=nodes)

@app.route('/create/iso', methods=['GET', 'POST'])
def iso():
    if request.method == "POST":
            node = request.form.get('node_name')
            isos = list_isos(proxmox, node)
    return render_template('createiso.html', isos=isos)