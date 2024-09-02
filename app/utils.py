from proxmoxer import ProxmoxAPI
import logging, time
from app.config import load_proxmox_config
import requests

def connect_to_proxmox():
    config = load_proxmox_config()
    if not config:
        return None

    try:
        proxmox = ProxmoxAPI(
            config['host'],
            user=config['user'],
            password=config['password'],
            verify_ssl=False,
            timeout=15
        )
        # Test the connection
        proxmox.nodes.get()
        return proxmox
    except requests.exceptions.SSLError:
        print("SSL Error: Certificate verification failed. If you're using a self-signed certificate, you may need to disable SSL verification.")
    except Exception as e:
        print(config)
        print(f"Error connecting to Proxmox: {str(e)}")
    return None

def list_vms_notemplate(proxmox):
    nodes = proxmox.nodes.get()
    vms_info = []
    for node in nodes:
        vms = proxmox.nodes(node['node']).qemu.get()
        for vm in vms:
                vm_info = {
                    'vmid': vm['vmid'],
                    'name': vm.get('name', f"VM {vm['vmid']}"),
                    'node': node['node'],
                    'status': vm.get('status'),
                    'config': proxmox.nodes(node['node']).qemu(vm['vmid']).config.get()
                }
                vms_info.append(vm_info)
    return (vm for vm in vms_info if vm['config'].get('template') != 1)

def list_vms_node(proxmox):
    nodes = proxmox.nodes.get()
    vms_info = []
    for node in nodes:
        vms = proxmox.nodes(node['node']).qemu.get()
        for vm in vms:
            vm_info = {
                'vmid': vm['vmid'],
                'name': vm.get('name', f"VM {vm['vmid']}"),
                'node': node['node']
            }
            vms_info.append(vm_info)
    return vms_info

def list_vms(proxmox):
    nodes = proxmox.nodes.get()
    for node in nodes:
        vms = proxmox.nodes(node['node']).qemu.get()
    return vms

# TODO - Arrumar o storage name de forma dinamica. Não quero adicionar mais um passo sem usar AJAX.
def list_isos(proxmox, node, storage_name="local"):
    isos = proxmox.nodes(node).storage(storage_name).content.get(content='iso')
    return [iso['volid'] for iso in isos]
    

def list_nodes(proxmox):
    nodes = proxmox.nodes.get()
    return [node['node'] for node in nodes]

def generate_unique_vm_id(proxmox):
    vms = proxmox.cluster.resources.get(type='vm')
    max_id = max([int(vm['vmid']) for vm in vms])
    return max_id + 1

def convert_template(proxmox, node, vm_id):
    try:
        proxmox.nodes(node).qemu(vm_id).config.put(template=1)
        print(f'VM {vm_id} converted to template.')
        return True
    except Exception as e:
        return False
    
def list_templates(proxmox):
    nodes = proxmox.nodes.get()
    templates = []
    for node_data in nodes:
        vms = proxmox.nodes(node_data['node']).qemu.get()
        for vm in vms:
            if vm.get('template') == 1:
                # Buscando a configuração da VM/template
                config = proxmox.nodes(node_data['node']).qemu(vm['vmid']).config.get()
                template_info = {
                    'vmid': vm['vmid'],
                    'name': vm.get('name', f"Template {vm['vmid']}"),
                    'node': node_data['node'],
                    'config': config
                }
                templates.append(template_info)
    return templates

def create_vm_from_template(proxmox, node, name, vm_id, template_id):
    try:
        # Obtém o nó do Proxmox
        node = proxmox.nodes(node)

        # Verifica se o template existe
        templates = node.qemu.get()
        if not any(vm['vmid'] == int(template_id) for vm in templates):
            raise ValueError(f"Template with ID {template_id} not found")

        # Cria um clone do template
        clone_params = {
            'newid': vm_id,
            'name': name,
            'full': 1,  # Full clone
            'storage': 'local-lvm',  # Ajuste conforme necessário
        }
        node.qemu(template_id).clone.post(**clone_params)

        print(f"VM '{name}' (ID: {vm_id}) created successfully from template {template_id}")
        return True

    except Exception as e:
        print(f"Error creating VM from template: {str(e)}")
        raise  

def start_vm(proxmox, node, vm_id):
    try:
        proxmox.nodes(node).qemu(vm_id).status.start.post()
        print(f"VM ID: {vm_id} started successfully")
        return True
    except Exception as e:
        print(f"Error starting VM: {str(e)}")

def get_vm_status(proxmox, node, vm_id):
    try:
        vm_status = proxmox.nodes(node).qemu(vm_id).status.current.get()
        return vm_status['status']
    except Exception as e:
        return f'Error retrieving VM status: {str(e)}'
    
def configure_cloud_init(proxmox, node, vm_id, username, password, ssh_key, ip_address):
    try:
        proxmox.nodes(node).qemu(vm_id).config.set(
            ciuser=username,
            cipassword=password,
            sshkeys=ssh_key,
            ipconfig0=f"ip={ip_address}/24,gw=192.168.1.1"
        )

        proxmox.nodes(node).qemu(vm_id).status.reboot.post()

        print(f"Cloud-Init configuration applied to VM ID: {vm_id}")
        return True

    except Exception as e:
        print(f"Error configuring Cloud-Init: {str(e)}")
        # Você pode querer registrar este erro em um sistema de logging
        raise  # Re-lança a exceção para ser tratada pelo chamador

# def check_auth():
#     if 'logged_in' not in session:
#         flash('Please log in to access this page', 'error')
#         return redirect(url_for('login'))