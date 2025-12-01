from Registry import Registry
import os
import sys
import re

def get_user_names(sam_path, verbose=False):
    try:
        registry = Registry.Registry(sam_path)
        users_key = registry.open("SAM\\Domains\\Account\\Users\\Names")
        if verbose:
            print(" [Info] Parsing Key : SAM\\Domains\\Account\\Users\\Names")

        print("User Accounts:")
        for user in users_key.subkeys():
            print(user.name())
    except Exception as e:
        print(f"Error accessing SAM hive: {e}")
        return []


def _get_default_value_bytes(key):
    for v in key.values():
        # python-registry represents the default value with an empty string name
        if v.name() == "" or v.name() is None:
            return v.value()
    return None

def get_user_sids(software_path, verbose=False):
    """
    Read the SOFTWARE hive for user SIDs.
    Can be found as keys SOFTWARE\Microsoft\Windows NT\CurrentVersion\ProfileList
    Each subkey is a user SID.
    Username is in the "ProfileImagePath" value.
    Returns a dict mapping SID to username.
    """
    sids = {}
    try:
        registry = Registry.Registry(software_path)
        users_root = registry.open('Microsoft\\Windows NT\\CurrentVersion\\ProfileList')
        
        if verbose:
            print(f" [Info] Parsing key: Microsoft\\Windows NT\\CurrentVersion\\ProfileList")
        
        for user_key in users_root.subkeys():
            sid = user_key.name()

            ## some SIDs are not user accounts, skip those
            ##if not re.match(r"S-1-5-21-\d+-\d+-\d+-\d+$", sid):
            #    continue
            
            try:
                # Get ProfileImagePath value
                profile_path_value = user_key.value("ProfileImagePath")
                profile_path = profile_path_value.value()
                
                if verbose:
                    print(f" [Info] Value Name: ProfileImagePath, Value Type: {profile_path_value.value_type_str()}")
                
                # Extract username from profile path (e.g., C:\Users\John -> John)
                username = os.path.basename(profile_path)
                sids[sid] = username
                
            except Registry.RegistryValueNotFoundException:
                # If ProfileImagePath doesn't exist, use SID as fallback
                sids[sid] = "(No profile path)"
                if verbose:
                    print(f" [Warning] ProfileImagePath not found for SID: {sid}")

    except Exception as e:
        print(f"Error reading SOFTWARE hive: {e}")

    return sids


## function to get user timestamps by username
##
## This function reads the SAM hive and retrieves user account timestamps
## such as last login time, password last set time, account creation time, etc.
##  
##.  HKLM\SAM\SAM\Domains\Account\Users\<User RID>
##
##.   Last Login Time: Offset 0x30 (8 bytes, Windows FILETIME)
##.   Password Last Set Time: Offset 0x38 (8 bytes, Windows FILETIME)
##.   Account Creation Time: Offset 0x40 (8 bytes, Windows FILETIME)
##