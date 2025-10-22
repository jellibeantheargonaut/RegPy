from Registry import Registry

def list_all_keys_recursive(hive_path, start_key=""):
    
    keys = []
    try:
        registry = Registry.Registry(hive_path)
        if start_key:
            root = registry.open(start_key)
        else:
            root = registry.root()
        def recurse(key, path):
            keys.append(path)
            for subkey in key.subkeys():
                recurse(subkey, f"{path}\\{subkey.name()}")
        recurse(root, start_key if start_key else "")
    except Exception as e:
        print(f"Error listing keys: {e}")
    return keys

def search_keys_by_keyword(hive_path, keyword, start_key=""):
    """
    Searches for registry keys containing the keyword in their path.
    Returns a list of matching key paths.
    """
    matches = []
    try:
        registry = Registry.Registry(hive_path)
        if start_key:
            root = registry.open(start_key)
        else:
            root = registry.root()
        def recurse(key, path):
            if keyword.lower() in path.lower():
                matches.append(path)
            for subkey in key.subkeys():
                recurse(subkey, f"{path}\\{subkey.name()}")
        recurse(root, start_key if start_key else "")
    except Exception as e:
        print(f"Error searching keys: {e}")
    return matches


## function for getting list of user installed applications from SAM hive

def get_installed_apps(hive_path,verbose=False):
    root_key = "Microsoft\\Windows\\CurrentVersion\\Uninstall"
    apps = []
    try:
        registry = Registry.Registry(hive_path)
        reg = registry.open(root_key)

        for subkey in reg.subkeys():
            try:
                info = {}
                info["KeyName"] = subkey.name()
                info["DisplayName"] = subkey.value("DisplayName").raw_data().decode()
                info["Publisher"] = subkey.value("Publisher").raw_data().decode()
                info["DisplayVersion"] = subkey.value("DisplayVersion").raw_data().decode()

                ## format InstallDate as YYYY-MM-DD if possible
                install_date = subkey.value("InstallDate").raw_data().decode()
                info["InstallDate"] = install_date
                info["InstallLocation"] = subkey.value("InstallLocation").raw_data().decode()
                info["UninstallString"] = subkey.value("UninstallString").raw_data().decode()
                info["EstimatedSizeKB"] = subkey.value("EstimatedSize").raw_data().decode()
                # If not verbose, append name only
                if verbose:
                    apps.append(info)
                else:
                    name = info.get("DisplayName") 
                    apps.append(name)
            except Exception:
                # skip problematic entries
                continue
    except Exception as e:
        print(f"Error accessing hive for installed apps: {e}")
    return apps

## function to get list of shrares from system hive

def get_shares(hive_path):
    shares = []
    try:
        registry = Registry.Registry(hive_path)
        shares_key = registry.open("ControlSet001\\Services\\LanmanServer\\Shares")

        for subkey in shares_key.subkeys():
            shares.append(subkey.name())
    except Exception as e:
        print(f"Error accessing SYSTEM hive for shares: {e}")
    return shares


## function to get drivers 
def get_drivers(hive_path):
    drivers = []
    try:
        registry = Registry.Registry(hive_path)
        drivers_key = registry.open("ControlSet001\\Services")

        for subkey in drivers_key.subkeys():
            try:
                start_value = subkey.value("Start").value()
                # Consider drivers with Start type 0, 1, or 2 as loaded drivers
                if start_value in (0, 1, 2):
                    drivers.append(subkey.name())
            except Exception:
                continue
    except Exception as e:
        print(f"Error accessing SYSTEM hive for drivers: {e}")
    return drivers

