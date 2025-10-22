from Registry import Registry
import ipaddress, binascii

def get_nic_names(system_path):
    nic_names = {}
    try:
        registry = Registry.Registry(system_path)
        interfaces_key = registry.open("ControlSet001\\Services\\Tcpip\\Parameters\\Interfaces")
        for nic_key in interfaces_key.subkeys():
            guid = nic_key.name()
            try:
                network_key_path = f"ControlSet001\\Control\\Network\\{{4D36E972-E325-11CE-BFC1-08002BE10318}}\\{guid}\\Connection"
                connection_key = registry.open(network_key_path)
                name = connection_key.value("Name").value()
                nic_names[guid] = name
            except Exception:
                nic_names[guid] = "(No friendly name found)"
    except Exception as e:
        print(f"Error accessing SYSTEM hive for NIC names: {e}")
    return nic_names


def get_nic_details(system_path, guid):
    details = {}
    try:
        registry = Registry.Registry(system_path)
        interface_key_path = f"ControlSet001\\Services\\Tcpip\\Parameters\\Interfaces\\{guid}"
        interface_key = registry.open(interface_key_path)
        for value in interface_key.values():
            if value.name() == "DhcpGatewayHardware":
                mac = binascii.hexlify(value.value()).decode()
                mac = mac[-12:]
                mac = ":".join(mac[i:i+2] for i in range(0, len(mac), 2))
                details["MAC Address"] = mac
            else:
                details[value.name()] = value.value()
        try:
            connection_key_path = f"ControlSet001\\Control\\Network\\{{4D36E972-E325-11CE-BFC1-08002BE10318}}\\{guid}\\Connection"
            connection_key = registry.open(connection_key_path)
            details["Name"] = connection_key.value("Name").value()
        except Exception:
            details["Name"] = "(No friendly name found)"
    except Exception as e:
        print(f"Error accessing SYSTEM hive for NIC details: {e}")
    return details