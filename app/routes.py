from flask import render_template, url_for, request, jsonify, flash, redirect, session, current_app as app
from app.utils import *
from app.forms import TemplateForm, CloudInitInstanceForm, RegisterForm, LoginForm, ProxmoxConfigForm
from app.auth import *
from app.config import save_proxmox_config, load_proxmox_config
import os, json, subprocess
import urllib.parse

proxmox = connect_to_proxmox()

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        if authenticate(username, password):
            session['logged_in'] = True
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials.', 'error')
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        save_user(username, password)
        flash('User registered successfully!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/proxmox_config', methods=['GET', 'POST'])
def proxmox_config():
    if 'logged_in' not in session:
        flash('Please log in to access this page', 'error')
        return redirect(url_for('login'))

    form = ProxmoxConfigForm()
    if form.validate_on_submit():
        save_proxmox_config(form.host.data, form.user.data, form.password.data, form.login_method.data)
        global proxmox
        proxmox = connect_to_proxmox()
        if proxmox:
            flash('Proxmox configuration saved and connected successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Proxmox configuration saved but connection failed. Please check your settings.', 'error')

    config = load_proxmox_config()
    if config:
        form.host.data = config['host']
        form.user.data = config['user']
    
    return render_template('proxmox_config.html', form=form)

@app.route('/')
def index():
    if 'logged_in' not in session:
        flash('Please log in to access this page', 'error')
        return redirect(url_for('hero'))
    if proxmox is None:
        flash('Proxmox is not configured. Please set up the configuration.', 'warning')
        return redirect(url_for('proxmox_config'))
    vms = list_vms_notemplate(proxmox)
    templates = list_templates(proxmox)
    return render_template('index.html', vms=vms, templates=templates)
@app.route('/create')
def create():
    return render_template('create.html')

@app.route('/create/template', methods=['GET', 'POST'])
def create_template():
    form = TemplateForm()
    templates = list_templates(proxmox)
    nodes = list_nodes(proxmox)
    
    if templates:
        form.template_id.choices = [(template['vmid'], f"{template['name']} (Node: {template['node']})") for template in templates]
    else:
        flash('No templates available.', 'warning')
    
    if nodes:
        form.vm_node.choices = [(node, node) for node in nodes]
    else:
        flash('No nodes available.', 'warning')
    
    if form.validate_on_submit():
        template_id = form.template_id.data
        vm_node = form.vm_node.data
        vm_name = form.vm_name.data
        vm_id = form.vm_id.data
        
        try:
            # Criar a VM de forma síncrona
            create_vm_from_template(proxmox, vm_node, vm_name, vm_id, template_id)
            
            # Redirecionar para a página de carregamento
            return redirect(url_for('loading', vm_id=vm_id, vm_node=vm_node))
        except Exception as e:
            flash(f'Error creating VM: {str(e)}', 'error')
            return redirect(url_for('create_template'))
    
    return render_template('createtemplate.html', form=form, templates=templates, nodes=nodes)

@app.route('/loading')
def loading():
    vm_id = request.args.get('vm_id')
    vm_node = request.args.get('vm_node')
    return render_template('loading.html', vm_id=vm_id, vm_node=vm_node)

@app.route('/check_vm_status/<vm_node>/<vm_id>')
def check_vm_status(vm_node, vm_id):
    status = get_vm_status(proxmox, vm_node, vm_id)
    return jsonify({'status': status})

@app.route('/start_vm/<vm_node>/<vm_id>')
def start_vm_route(vm_node, vm_id):
    start_vm(proxmox, vm_node, vm_id)
    return redirect(url_for('index'))

@app.route('/convert-to-template', methods=['GET', 'POST'])
def convert_to_template():
    if request.method == 'POST':
        vm_id = request.form.get('vm_id')
        if vm_id:
            node = None
            for vm in list_vms_node(proxmox):
                if str(vm['vmid']) == vm_id:
                    node = vm['node']
                    break
            
            if node:
                try:
                    proxmox.nodes(node).qemu(vm_id).config.put(template=1)
                    
                    flash('VM converted to template successfully!', 'success')
                    return redirect(url_for('index'))
                except Exception as e:
                    flash(f'Error converting VM to template: {str(e)}', 'error')

    vms = list_vms_node(proxmox)
    return render_template('convert_to_template.html', vms=vms)

@app.route('/create/cloud-init', methods=['GET', 'POST'])
def create_cloud_init():
    form = CloudInitInstanceForm()
    vm_id = request.args.get('vm_id')
    vm_node = request.args.get('vm_node')
    print(f"Received vm_id: {vm_id}, vm_node: {vm_node}")
    if form.validate_on_submit():
        encoded_ssh_key = urllib.parse.quote(form.ssh_key.data.strip())
        try:
            config = {
                'ciuser': form.username.data,
                'cipassword': form.password.data,
                'sshkeys': encoded_ssh_key,
                'ipconfig0': f"ip={form.ip_address.data}/24,gw=192.168.1.1"
            }
            print(f"Applying config to vm_id: {vm_id}, vm_node: {vm_node} with config: {config}")
            proxmox.nodes(vm_node).qemu(vm_id).config.post(**config)
            flash('Cloud-init configuration applied successfully!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'Error applying cloud-init configuration: {str(e)}', 'error')
    return render_template('createcloudinit.html', form=form, vm_id=vm_id, vm_node=vm_node)


# HERO PAGE E LOGINS:

@app.route('/hero')
def hero():
    return render_template('hero.html')

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     form = LoginForm()
#     if request.method == 'POST':
#         username = request.form.get('username')
#         password = request.form.get('password')
        
#         if authenticate(username, password):
#             flash('Login successful!', 'success')
#             return redirect(url_for('index'))
#         else:
#             flash('Invalid credentials.', 'error')
    
#     return render_template('login.html', form=form)

# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     form = RegisterForm()
#     if request.method == 'POST':
#         username = request.form.get('username')
#         password = request.form.get('password')
#         if not form.validate_on_submit():
#             flash('Invalid form data.', 'error')
#             return redirect(url_for('register'))
#         save_user(username, password)
#         flash('User registered successfully!', 'success')
#         return redirect(url_for('login'))
    
#     return render_template('register.html', form=form)