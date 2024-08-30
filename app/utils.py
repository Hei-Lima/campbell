from proxmoxer import ProxmoxAPI

def connect_to_proxmox():
    proxmox = ProxmoxAPI(
        '192.168.122.11', 
        user='root@pam', 
        password='heitorlindo', 
        verify_ssl=False
    )
    return proxmox

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