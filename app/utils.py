from proxmoxer import ProxmoxAPI

def connect_to_proxmox():
    proxmox = ProxmoxAPI(
        '192.168.122.11', 
        user='root@pam', 
        password='heitorlindo', 
        verify_ssl=False
    )
    return proxmox

proxmox = connect_to_proxmox()

def list_vms():
    nodes = proxmox.nodes.get()
    for node in nodes:
        vms = proxmox.nodes(node['node']).qemu.get()
    return vms
