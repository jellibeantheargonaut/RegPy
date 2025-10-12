from Registry import Registry
import os
import sys

def get_user_names(sam_path):
    try:
        registry = Registry.Registry(sam_path)
        users_key = registry.open("SAM\\Domains\\Account\\Users\\Names")

        print("User Accounts:")
        for user in users_key.subkeys():
            print(user.name())
    except Exception as e:
        print(f"Error accessing SAM hive: {e}")
        return []

def get_user_sids(sam_path):
    """
    Returns a dictionary mapping usernames to their SIDs from the SAM hive.
    """
    user_sids = {}
    try:
        registry = Registry.Registry(sam_path)
        names_key = registry.open("SAM\\Domains\\Account\\Users\\Names")
        for user_key in names_key.subkeys():
            username = user_key.name()
            # The RID is the name of the parent key of the username key
            rid = user_key.value("").value()
            # Build the full SID: S-1-5-21-...-RID
            # The domain SID is stored in "SAM\\Domains\\Account"
            account_key = registry.open("SAM\\Domains\\Account")
            domain_sid = account_key.value("V").value()
            # For simplicity, just return the RID for now
            user_sids[username] = rid
    except Exception as e:
        print(f"Error accessing SAM hive for SIDs: {e}")
    return user_sids