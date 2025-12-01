# RegPy - A Python-based Windows Registry Parser

RegPy is a lightweight, cross-platform tool for parsing and analyzing Windows registry hive files without requiring a Windows system. It's designed for digital forensics, incident response, and system analysis.

## Features

### User Account Analysis
- List all user accounts from SAM hive
- Extract user SIDs (Security Identifiers)

### Network Information
- List all network interface controllers (NICs)
- Get detailed NIC information (IP, MAC address, DHCP settings)
- Extract DNS server configurations
- View network adapter settings

### System Information
- Get Windows version and build information
- List installed applications
- Enumerate shared folders
- List system drivers
- View system services and their configurations

### Registry Operations
- List all keys in a hive recursively
- Search for keys by keyword
- Get all values under a specific key
- Support for SAM, SYSTEM, SOFTWARE, SECURITY, and NTUSER.DAT hives


## Installation

### Prerequisites
- Python 3.7 or higher
- `python-registry` library

### Install Dependencies

```bash
pip install python-registry
```

### Clone Repository

```bash
git clone https://github.com/jellibeantheargonaut/RegPy.git
cd RegPy
```

## Usage

### Command-Line Mode

#### Basic Usage

```bash
# Show help
python regpy.py -h

# List users from SAM hive
python regpy.py --sam /path/to/SAM --list-users

# Get Windows version (verbose mode)
python regpy.py --software /path/to/SOFTWARE --winver -V

# List network interfaces
python regpy.py --system /path/to/SYSTEM --list-nics

# Get NIC details by GUID
python regpy.py --system /path/to/SYSTEM --nic-details "{GUID}"

# List installed applications
python regpy.py --software /path/to/SOFTWARE --list-installed-applications

# Search for registry keys
python regpy.py --software /path/to/SOFTWARE --search "Microsoft"

# Get values from a specific key
python regpy.py --software /path/to/SOFTWARE -k "Microsoft\Windows NT\CurrentVersion" --get-values
```

#### User Operations

```bash
# List all users
python regpy.py --sam /path/to/SAM --list-users

# Get user SIDs
python regpy.py --sam /path/to/SAM --user-sids
```

#### Network Operations

```bash
# List network interfaces
python regpy.py --system /path/to/SYSTEM --list-nics

# Get NIC details
python regpy.py --system /path/to/SYSTEM --nic-details "{GUID}"

# List DNS servers
python regpy.py --system /path/to/SYSTEM --list-dns
```

#### System Information

```bash
# Get Windows version
python regpy.py --software /path/to/SOFTWARE --winver

# List installed applications
python regpy.py --software /path/to/SOFTWARE --list-installed-applications

# List shared folders
python regpy.py --system /path/to/SYSTEM --list-shares

# List drivers
python regpy.py --system /path/to/SYSTEM --list-drivers
```

#### Registry Operations

```bash
# List all keys in a hive
python regpy.py --software /path/to/SOFTWARE --list-all-keys

# List subkeys of a specific key
python regpy.py --software /path/to/SOFTWARE --subkeys "Microsoft\Windows"

# Get values from a key
python regpy.py --software /path/to/SOFTWARE -k "Microsoft\Windows NT\CurrentVersion" --get-values -V

# Search for keys containing keyword
python regpy.py --software /path/to/SOFTWARE --search "Uninstall"
```


## Command-Line Arguments

### Hive Files
- `--sam <path>` - Path to SAM hive file
- `--system <path>` - Path to SYSTEM hive file
- `--software <path>` - Path to SOFTWARE hive file
- `--security <path>` - Path to SECURITY hive file
- `--ntuser <path>` - Path to NTUSER.DAT hive file

### General Options
- `-V, --verbose` - Enable verbose output
- `-i, --interactive` - Start interactive shell mode

### User Operations
- `--list-users` - List all user accounts
- `--user-sids` - List user SIDs

### Network Operations
- `--list-nics` - List network interfaces
- `--nic-details <GUID>` - Get NIC details by GUID
- `--list-dns` - List DNS servers

### System Operations
- `--winver` - Get Windows version
- `--list-installed-applications` - List installed applications
- `--list-shares` - List shared folders
- `--list-drivers` - List drivers

### Registry Operations
- `-k, --key <path>` - Registry key to parse
- `--get-values` - Get all values under specified key
- `--list-all-keys` - List all keys in hive
- `--subkeys <path>` - List subkeys of specified key
- `--search <keyword>` - Search for keys containing keyword


## Examples

### Extract User Information

```bash
# Get all user accounts
python regpy.py --sam SAM --list-users

# Get user SIDs with verbose output
python regpy.py --software SOFTWARE --user-sids -V
```

### Network Forensics

```bash
# List all network adapters
python regpy.py --system SYSTEM --list-nics

# Get detailed info for a specific NIC
python regpy.py --system SYSTEM --nic-details "{12345678-1234-1234-1234-123456789012}"

# Extract DNS configuration
python regpy.py --system SYSTEM --list-dns
```

### System Analysis

```bash
# Get Windows version and build
python regpy.py --software SOFTWARE --winver -V

# List all installed software
python regpy.py --software SOFTWARE --list-installed-applications

# Find all Microsoft products
python regpy.py --software SOFTWARE --search "Microsoft"
```


## Hive File Locations (on Windows)

Common registry hive locations on Windows systems:

```
C:\Windows\System32\config\SAM
C:\Windows\System32\config\SYSTEM
C:\Windows\System32\config\SOFTWARE
C:\Windows\System32\config\SECURITY
C:\Users\<username>\NTUSER.DAT
```

## Use Cases

- **Digital Forensics**: Analyze registry hives from forensic images
- **Incident Response**: Extract system information without booting Windows
- **Malware Analysis**: Examine registry modifications
- **System Auditing**: Review installed software and configurations
- **Cross-Platform Analysis**: Parse Windows registry on Linux/macOS

## Limitations

- Read-only operations (no registry modification)
- Some advanced registry features not yet implemented
- Requires offline hive files (not for live system analysis)

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## Author

**@jellibeantheargonaut**

## License

This project is open source. Please check the repository for license details.

## Acknowledgments

- Built using the [python-registry](https://github.com/williballenthin/python-registry) library by Willi Ballenthin
- Inspired by the need for cross-platform Windows registry analysis tools