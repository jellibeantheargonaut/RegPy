import argparse
import os
import sys

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
    parser.add_argument('hive', help='Path to the registry hive file')
    parser.add_argument('-o', '--output', help='Output file to save results', default=None)
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    

    if len(sys.argv) == 1:
        print(BANNER)
        parser.print_help()
        return

    args = parser.parse_args()

if __name__ == "__main__":
    main()