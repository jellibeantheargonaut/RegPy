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

def get_shares(hive_path, verbose=False):
    shares = []
    try:
        registry = Registry.Registry(hive_path)
        shares_key = registry.open("ControlSet001\\Services\\LanmanServer\\Shares")

        if verbose:
            print(" [Info] Parsing Key : ControlSet001\\Services\\LanmanServer\\Shares")

        for subkey in shares_key.subkeys():
            if verbose:
                print(f" [Info] Found Share: {subkey.name()}")
            shares.append(subkey.name())
    except Exception as e:
        print(f"Error accessing SYSTEM hive for shares: {e}")
    return shares


## function to get drivers 
def get_drivers(hive_path, verbose=False):
    drivers = []
    try:
        registry = Registry.Registry(hive_path)
        drivers_key = registry.open("ControlSet001\\Services")

        if verbose:
            print(" [Info] Parsing Key : ControlSet001\\Services")

        for subkey in drivers_key.subkeys():
            try:
                if verbose:
                    print(f" [Info] Found Driver: {subkey.name()}")
                start_value = subkey.value("Start")

                if verbose:
                    print(f" [Info] Value Name: Start, Value Type: DWORD ( {subkey.value('Start').value_type_str()} )")
                    print(f" [Info] Value Data: {start_value.value()}")
                # Consider drivers with Start type 0, 1, or 2 as loaded drivers
                if start_value.value() in (0, 1, 2):
                    drivers.append(subkey.name())
            except Exception:
                continue
    except Exception as e:
        print(f"Error accessing SYSTEM hive for drivers: {e}")
    return drivers


## auxiliary function to convert time from unix timestamp
def _convert_install_time(val):
    from datetime import datetime
    dt_object = datetime.fromtimestamp(val)
    human_readable = dt_object.strftime("%Y-%m-%d %H:%M:%S")
    return human_readable

## function to get the windows version from SYSTEM hive
def get_windows_version(hive_path, verbose=False):
    try:
        data = {}
        registry = Registry.Registry(hive_path)
        current_version_key = registry.open('Microsoft\\Windows NT\\CurrentVersion')

        ## verbose output
        if verbose:
            print(f" [Info] Parsing key: Microsoft\\Windows NT\\CurrentVersion")

        product_name = current_version_key.value("ProductName")
        if verbose:
            print(f" [Info] Value Name: ProductName, Value Type: String ( {product_name.value_type_str()} )")
            print(f" [Info] Value Data: {product_name.value()}")

        registered_owner = current_version_key.value("RegisteredOwner")
        if verbose:
            print(f" [Info] Value Name: RegisteredOwner, Value Type: String ( {registered_owner.value_type_str()} )")
            print(f" [Info] Value Data: {registered_owner.value()}")

        lcuver = current_version_key.value("LCUVer")
        if verbose:
            print(f" [Info] Value Name: LCUVer, Value Type: String ( {lcuver.value_type_str()} )")
            print(f" [Info] Value Data: {lcuver.value()}")

        current_build = current_version_key.value("CurrentBuild")
        if verbose:
            print(f" [Info] Value Name: CurrentBuild, Value Type: String ( {current_build.value_type_str()} )")
            print(f" [Info] Value Data: {current_build.value()}")

        current_version = current_version_key.value("CurrentVersion")
        if verbose:
            print(f" [Info] Value Name: CurrentVersion, Value Type: String ( {current_version.value_type_str()} )")
            print(f" [Info] Value Data: {current_version.value()}")
            print(" ",end="\n")


        ## convert install_time to a readable format
        install_time = current_version_key.value("InstallDate").value()
        data["ProductName"] = product_name.value()
        data["RegisteredOwner"] = registered_owner.value()
        data["LCUVer"] = lcuver.value()

        data["CurrentBuild"] = current_build.value()
        data["CurrentVersion"] = current_version.value()
        data["InstallDate"] = _convert_install_time(install_time)
        return data
    except Exception as e:
        print(f"Error accessing SYSTEM hive for Windows version: {e}")
        return None