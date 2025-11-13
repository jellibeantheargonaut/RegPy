from Registry import Registry
import os
import sys
import re

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
    Read the SAM hive at `sam_path` and return a dict mapping RID hex
    (e.g. '000001F4') -> full SID string (e.g. 'S-1-5-21-...-500') or None if
    a SID couldn't be parsed for that RID.
    """

    """
       Need to work on this function later
    """
    sids = {}
    try:
        registry = Registry.Registry(sam_path)
        users_root = registry.open(r"SAM\Domains\Account\Users")

        for subkey in users_root.subkeys():
            name = subkey.name()
            # RID subkeys are typically 8-hex-digit names (skip Names, etc.)
            if not isinstance(name, str) or not re.fullmatch(r"[0-9A-Fa-f]{8}", name):
                continue

            v_bytes = _get_default_value_bytes(subkey)
            try:
                rid_decimal = int(name, 16)
            except ValueError:
                sids[name] = None
                continue

            sid = _parse_sid_from_bytes(v_bytes) if v_bytes else None

            if sid:
                # Ensure the SID ends with the RID in decimal form
                if sid.endswith(f"-{rid_decimal}"):
                    full_sid = sid
                else:
                    full_sid = f"{sid}-{rid_decimal}"
                sids[name] = full_sid
            else:
                sids[name] = None
    except Exception as e:
        # Keep behaviour simple for callers: print the error and return
        # whatever we've collected so far (likely empty)
        print(f"Error reading SAM hive: {e}")

    return sids