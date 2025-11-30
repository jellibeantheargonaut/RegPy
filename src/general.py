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

    ## if key not found or also check Microsoft\\Windows\\CurrentVersion\\App Paths

    apps = []
    try:
        registry = Registry.Registry(hive_path)
        reg = registry.open(root_key)

        for subkey in reg.subkeys():
            try:
                info = {}
                info["KeyName"] = subkey.name()
                
                # If verbose, try to get all available values
                if verbose:
                    # Helper function to safely get value
                    def safe_get_value(key, value_name):
                        try:
                            return key.value(value_name).value()
                        except:
                            return "(not set)"
                    
                    info["DisplayName"] = safe_get_value(subkey, "DisplayName")
                    info["Publisher"] = safe_get_value(subkey, "Publisher")
                    info["DisplayVersion"] = safe_get_value(subkey, "DisplayVersion")
                    
                    # Format InstallDate as YYYY-MM-DD if possible
                    install_date = safe_get_value(subkey, "InstallDate")
                    if install_date != "(not set)" and len(install_date) == 8:
                        # Format YYYYMMDD to YYYY-MM-DD
                        try:
                            info["InstallDate"] = f"{install_date[0:4]}-{install_date[4:6]}-{install_date[6:8]}"
                        except:
                            info["InstallDate"] = install_date
                    else:
                        info["InstallDate"] = install_date
                    
                    info["InstallLocation"] = safe_get_value(subkey, "InstallLocation")
                    info["UninstallString"] = safe_get_value(subkey, "UninstallString")
                    
                    # EstimatedSize is DWORD, handle differently
                    try:
                        size_kb = subkey.value("EstimatedSize").value()
                        info["EstimatedSizeKB"] = str(size_kb)
                    except:
                        info["EstimatedSizeKB"] = "(not set)"
                    
                    apps.append(info)
                else:
                    # Non-verbose: try DisplayName first, fall back to KeyName
                    try:
                        name = subkey.value("DisplayName").value()
                    except:
                        name = info.get("KeyName")
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


## function to get the services from system hive
def get_services(hive_path, verbose=False):
    services = []
    try:
        registry = Registry.Registry(hive_path)
        services_key = registry.open("ControlSet001\\Services")

        if verbose:
            print(" [Info] Parsing Key : ControlSet001\\Services")

        for subkey in services_key.subkeys():
            if verbose:
                print(f" [Info] Found Service: Key : ControlSet001\\Services\\{subkey.name()}")
            services.append(subkey.name())
    except Exception as e:
        print(f"Error accessing SYSTEM hive for services: {e}")
    return services

## function to get the details of a specific service by name
def get_service_details(hive_path, service_name, verbose=False):
    try:
        registry = Registry.Registry(hive_path)
        service_key_path = f"ControlSet001\\Services\\{service_name}"
        service_key = registry.open(service_key_path)

        if verbose:
            print(f" [Info] Parsing Key : {service_key_path}")

        details = {}
        for value in service_key.values():
            details[value.name()] = value.value()
            if verbose:
                print(f" [Info] Value Name: {value.name()}, Value Type: {value.value_type_str()}")
                print(f" [Info] Value Data: {value.value()}")
        return details
    except Exception as e:
        print(f"Error accessing SYSTEM hive for service details: {e}")
        return None


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

        ##lcuver = current_version_key.value("LCUVer")
        ##if verbose:
        ##    print(f" [Info] Value Name: LCUVer, Value Type: String ( {lcuver.value_type_str()} )")
        ##    print(f" [Info] Value Data: {lcuver.value()}")

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
        ##data["LCUVer"] = lcuver.value()

        data["CurrentBuild"] = current_build.value()
        data["CurrentVersion"] = current_version.value()
        data["InstallDate"] = _convert_install_time(install_time)
        return data
    except Exception as e:
        print(f"Error accessing SYSTEM hive for Windows version: {e}")
        return None


### functions to directly query the hives for keys and stuff

## function to list the values under a given key
## fucntion to get the values under a given key or a specific value in a key

def get_key_values(hive_path, key_path, verbose=False):
    values_dict = {}
    try:
        registry = Registry.Registry(hive_path)
        key = registry.open(key_path)

        if verbose:
            print(f" [Info] Parsing Key : {key_path}")

        for value in key.values():
            values_dict[value.name()] = value.value()
            if verbose:
                print(f" [Info] Value Name: {value.name()}, Value Type: {value.value_type_str()}")
                print(f" [Info] Value Data: {value.value()}")
    except Exception as e:
        print(f"Error accessing hive for key values: {e}")
    return values_dict


## function to export the whole hive in a csv, or json format