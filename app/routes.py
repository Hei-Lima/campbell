from flask import render_template, url_for, request, jsonify, flash, redirect, current_app as app
from app.utils import *
from app.forms import TemplateForm, CloudInitInstanceForm
import os, json, subprocess

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

def get_vm_status(proxmox, node, vm_id):
    try:
        vm = proxmox.nodes(node).qemu(vm_id).status.current.get()
        return vm['status']
    except Exception as e:
        return 'unknown'

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


# @app.route('/template', methods=['GET', 'POST'])
# def template():
#     form = VMTemplateForm()
#     if form.validate_on_submit():
#         form_data = {
#             'template_name': form.template_name.data,
#             'cpu_cores': form.cpu_cores.data,
#             'memory': form.memory.data,
#             'disk_size': form.disk_size.data,
#             'network_adapter': form.network_adapter.data,
#             'os_type': form.os_type.data
#         }
        
#         json_file_path = app.config['JSON_FILE_PATH']
#         if os.path.exists(json_file_path):
#             try:
#                 with open(json_file_path, 'r') as file:
#                     data = json.load(file)
#             except json.JSONDecodeError:
#                 data = {"templates": []}
#         else:
#             data = {"templates": []}
        
#         data['templates'].append(form_data)
        
#         with open(json_file_path, 'w') as file:
#             json.dump(data, file, indent=4)

#         flash('VM template generated successfully!', 'success')
#         return redirect(url_for('index'))
    
#     with open(app.config['JSON_FILE_PATH'], 'r') as file:
#         data = json.load(file)
#     templates = data.get('templates', [])
#     print(templates)

#     return render_template('template.html', form=form, templates=templates)

@app.route('/create-instance', methods=['GET', 'POST'])
def create_instance():
    form = CloudInitInstanceForm()

    # Carregar templates disponíveis
    try:
        with open(app.config['JSON_FILE_PATH'], 'r') as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        flash(f'Error loading templates: {str(e)}', 'error')
        return redirect(url_for('create_instance'))
    
    templates = data['templates']
    form.template.choices = [(t['template_name'], t['template_name']) for t in templates]

    if form.validate_on_submit():
        template = next((t for t in templates if t['template_name'] == form.template.data), None)
        if template:
            # Gerar um ID único para a nova VM
            vm_id = generate_unique_vm_id(proxmox)

            try:
                # Clonar o template para criar uma nova VM
                proxmox.nodes(template['node']).qemu(template['template_id']).clone(
                    newid=vm_id,
                    name=form.hostname.data
                )

                # Configurar Cloud-Init
                proxmox.nodes(template['node']).qemu(vm_id).config.set(
                    ciuser=form.username.data,
                    cipassword=form.password.data,
                    sshkeys=form.ssh_key.data,
                    ipconfig0=f"ip={form.ip_address.data}/24,gw=192.168.1.1"
                )

                # Iniciar a VM
                proxmox.nodes(template['node']).qemu(vm_id).status.start.post()

                flash('Cloud-init instance created successfully!', 'success')
                return redirect(url_for('index'))
            except Exception as e:
                flash(f'Error creating instance: {str(e)}', 'error')

    return render_template('createinstance.html', form=form)

