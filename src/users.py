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

def _parse_sid_from_bytes(data):
    """
    Try to find a SID structure in the given byte blob and return it as a string (e.g. S-1-5-21-...).
    Returns None if no plausible SID is found.
    """
    if not data or not isinstance(data, (bytes, bytearray)):
        return None
    length = len(data)
    for i in range(0, length - 8):
        try:
            # SID structure: 1 byte revision (should be 1), 1 byte subauth count,
            # 6 bytes identifier authority (big-endian), then subauth_count * 4 bytes (little-endian)
            revision = data[i]
            sub_count = data[i + 1]
            if revision != 1 or sub_count < 1 or sub_count > 15:
                continue
            if i + 8 + 4 * sub_count > length:
                continue
            id_auth = int.from_bytes(data[i + 2:i + 8], byteorder='big', signed=False)
            subauths = []
            for j in range(sub_count):
                start = i + 8 + j * 4
                sub = int.from_bytes(data[start:start + 4], byteorder='little', signed=False)
                subauths.append(str(sub))
            sid = f"S-1-{id_auth}"
            if subauths:
                sid = sid + "-" + "-".join(subauths)
            return sid
        except Exception:
            continue
    return None

def _get_default_value_bytes(key):
    for v in key.values():
        # python-registry represents the default value with an empty string name
        if v.name() == "" or v.name() is None:
            return v.value()
    return None

def get_user_sids(sam_path):
    """
    Returns a dictionary mapping usernames to their full SIDs (best-effort).
    If the domain SID can be parsed from the SAM 'V' value, the full SID is returned (S-1-...-RID).
    Otherwise returns 'RID:<rid>' where rid is the relative id.
    """
    user_sids = {}
    try:
        registry = Registry.Registry(sam_path)
        names_key = registry.open("SAM\\Domains\\Account\\Users\\Names")
        account_key = registry.open("SAM\\Domains\\Account")

        # Try to parse domain SID from the 'V' value (binary blob)
        domain_sid = None
        try:
            v_blob = account_key.value("V").value()
            domain_sid = _parse_sid_from_bytes(v_blob)
        except Exception:
            domain_sid = None

        for user_key in names_key.subkeys():
            username = user_key.name()
            try:
                default_bytes = _get_default_value_bytes(user_key)
                rid = None
                if isinstance(default_bytes, (bytes, bytearray)):
                    # The default value usually contains the RID in the first 4 bytes (little-endian)
                    if len(default_bytes) >= 4:
                        rid = int.from_bytes(default_bytes[:4], byteorder='little', signed=False)
                    else:
                        rid = int.from_bytes(default_bytes, byteorder='little', signed=False)
                elif isinstance(default_bytes, int):
                    rid = default_bytes
                else:
                    # fallback: try to cast
                    rid = int(default_bytes)
                if domain_sid:
                    full_sid = f"{domain_sid}-{rid}"
                else:
                    full_sid = f"RID:{rid}"
                user_sids[username] = full_sid
            except Exception as e:
                user_sids[username] = "(error parsing RID)"
    except Exception as e:
        print(f"Error accessing SAM hive for SIDs: {e}")
    return user_sids