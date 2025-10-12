import argparse
import os
import sys

## import other files here
from src.users import *
from src.network import *

BANNER = r"""

██████  ███████  ██████  ██████  ██    ██ 
██   ██ ██      ██       ██   ██  ██  ██  
██████  █████   ██   ███ ██████    ████   
██   ██ ██      ██    ██ ██         ██    
██   ██ ███████  ██████  ██         ██    

=============================================                                       
RegPy - A Python-based Registry Parser
Author: @jellibeantheargonaut
=============================================
"""

def main():
    parser = argparse.ArgumentParser(description='RegPy - A Python-based Registry Parser')

    parser.add_argument('--sam', type=str, help='Path to SAM hive file')
    parser.add_argument('--system', type=str, help='Path to SYSTEM hive file')
    parser.add_argument('--security', type=str, help='Path to SECURITY hive file')
    parser.add_argument('--software', type=str, help='Path to SOFTWARE hive file')
    parser.add_argument('--ntuser', type=str, help='Path to NTUSER.DAT hive file')
    parser.add_argument('-k', '--key', type=str, help='Registry key to parse')
    parser.add_argument('-r', '--recursive', action='store_true', help='Recursively parse subkeys')
    parser.add_argument('--subkeys', action='store_true', help='List all subkeys of the specified key')
    parser.add_argument('--regex', type=str, help='Regex pattern to filter keys/values')
    parser.add_argument('--json', action='store_true', help='Output results in JSON format')
    parser.add_argument('--csv', action='store_true', help='Output results in CSV format')

    ## Windows specific options
    parser.add_argument('--winver', help="Get Windows version from the registry file")
    parser.add_argument('--user-sids', action='store_true', help="List all user SIDs in the registry file")
    
    ## Windows network options
    parser.add_argument('--list-nics', action='store_true', help="List all network interfaces")
    parser.add_argument('--nic-details', type=str, help="Get details of a network interface by GUID")
    parser.add_argument('--nic-by-mac', type=str, help="Get network interface details by MAC address")
    parser.add_argument('--nic-by-ip', type=str, help="Get network interface details by IP address")
    parser.add_argument('--list-dns', action='store_true', help="List DNS servers")

    ## Windows user options
    parser.add_argument('--list-users', action='store_true', help="List all user accounts")
    parser.add_argument('--user-details', type=str, help="Get details of a user by username")
    parser.add_argument('--list-autoruns', action='store_true', help="List all autorun entries")
    parser.add_argument('--list-installed-software', action='store_true', help="List all installed software")
    parser.add_argument('--software-details', type=str, help="Get details of installed software by name")
    parser.add_argument('--list-services', action='store_true', help="List all services")
    parser.add_argument('--service-details', type=str, help="Get details of a service by name")
    parser.add_argument('--list-drivers', action='store_true', help="List all drivers")
    parser.add_argument('--driver-details', type=str, help="Get details of a driver by name")
    parser.add_argument('--list-shares', action='store_true', help="List all shared folders")
    parser.add_argument('--list-mapped-drives', action='store_true', help="List all mapped network drives")
    

    if len(sys.argv) == 1:
        print(BANNER)
        parser.print_help()
        return

    args = parser.parse_args()

    ## Test get_user_names_from_sam function
    if args.sam and args.list_users:
        get_user_names(args.sam)

    ## Test get_nic_names function
    if args.system and args.list_nics:
        nic_names = get_nic_names(args.system)
        for guid, name in nic_names.items():
            print(f"{guid}: {name}")

    ## Test get_nic_details function
    if args.nic_details and args.system:
        print(BANNER)
        details = get_nic_details(args.system, args.nic_details)
        print(f"Details for NIC {args.nic_details}:")
        for k, v in details.items():
            print(f"{k}: {v}")
    
if __name__ == "__main__":
    main()