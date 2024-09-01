from proxmoxer import ProxmoxAPI
import logging, time

def connect_to_proxmox():
    proxmox = ProxmoxAPI(
        '192.168.122.11', 
        user='root@pam', 
        password='heitorlindo', 
        verify_ssl=False, 
        timeout=15
    )
    return proxmox

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
                template_info = {
                    'vmid': vm['vmid'],
                    'name': vm.get('name', f"Template {vm['vmid']}"),
                    'node': node_data['node']
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
            'storage': 'local',  # Ajuste conforme necessário
        }
        task = node.qemu(template_id).clone.post(**clone_params)

        # Aguarda a conclusão da tarefa de clonagem
        while not proxmox.nodes(node.name).tasks(task).status.get()['status'] == 'stopped':
            time.sleep(1)

        # Inicia a VM recém-criada
        node.qemu(vm_id).status.start.post()

        print(f"VM '{name}' (ID: {vm_id}) created successfully from template {template_id}")
        return True

    except Exception as e:
        print(f"Error creating VM from template: {str(e)}")
        # Você pode querer registrar este erro em um sistema de logging
        raise  # Re-lança a exceção para ser tratada pelo chamador

    
def get_vm_status(proxmox, node, vm_id):
    try:
        vm_status = proxmox.nodes(node).qemu(vm_id).status.current.get()
        return vm_status['status']
    except Exception as e:
        return f'Error retrieving VM status: {str(e)}'