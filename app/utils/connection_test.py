import socket
import subprocess
import psutil
import requests
import sys
from typing import Dict, List, Tuple

def check_port_in_use(port: int = 8050) -> Tuple[bool, str]:
    """Check if port is already in use"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', port))
            return False, "Port is available"
    except OSError:
        # Find process using the port
        for proc in psutil.process_iter(['pid', 'name', 'connections']):
            try:
                for conn in proc.connections():
                    if conn.laddr.port == port:
                        return True, f"Port {port} is being used by {proc.name()} (PID: {proc.pid})"
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return True, f"Port {port} is in use but process could not be identified"

def check_firewall_status() -> Dict[str, bool]:
    """Check Windows Firewall status"""
    try:
        # Check firewall status
        result = subprocess.run(
            'netsh advfirewall show allprofiles',
            shell=True,
            capture_output=True,
            text=True
        )
        
        output = result.stdout.lower()
        profiles = ['domain', 'private', 'public']
        status = {}
        
        for profile in profiles:
            status[profile] = 'state                                 on' in output
            
        return status
    except Exception as e:
        print(f"Error checking firewall status: {e}")
        return {profile: None for profile in profiles}

def check_dashboard_rule() -> List[Dict[str, str]]:
    """Check HighTierDashboard firewall rules"""
    try:
        result = subprocess.run(
            'netsh advfirewall firewall show rule name="HighTierDashboard"',
            shell=True,
            capture_output=True,
            text=True
        )
        
        if "No rules match the specified criteria" in result.stdout:
            return []
            
        rules = []
        current_rule = {}
        
        for line in result.stdout.split('\n'):
            line = line.strip()
            if not line:
                if current_rule:
                    rules.append(current_rule)
                    current_rule = {}
                continue
                
            if ':' in line:
                key, value = line.split(':', 1)
                current_rule[key.strip()] = value.strip()
                
        if current_rule:
            rules.append(current_rule)
            
        return rules
    except Exception as e:
        print(f"Error checking firewall rules: {e}")
        return []

def test_local_connection(port: int = 8050) -> bool:
    """Test if we can connect to localhost"""
    try:
        response = requests.get(f"http://localhost:{port}", timeout=2)
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        return False
    except Exception:
        return False

def get_ip_addresses() -> List[str]:
    """Get all IP addresses of the machine"""
    ips = []
    try:
        # Get hostname first
        hostname = socket.gethostname()
        # Get IP by hostname
        ips.append(socket.gethostbyname(hostname))
        
        # Get all network interfaces
        for interface, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family == socket.AF_INET:  # IPv4
                    ips.append(addr.address)
    except Exception as e:
        print(f"Error getting IP addresses: {e}")
    return list(set(ips))  # Remove duplicates

def main():
    """Run all connection tests"""
    PORT = 8050
    
    print("\nCall Center Dashboard - Connection Diagnostics")
    print("-" * 50)
    
    # 1. Check if port is in use
    print("\n1. Checking port status...")
    in_use, port_message = check_port_in_use(PORT)
    print(port_message)
    
    # 2. Check firewall status
    print("\n2. Checking firewall status...")
    fw_status = check_firewall_status()
    for profile, enabled in fw_status.items():
        print(f"  {profile.capitalize()} Profile: {'Enabled' if enabled else 'Disabled'}")
    
    # 3. Check dashboard firewall rules
    print("\n3. Checking dashboard firewall rules...")
    rules = check_dashboard_rule()
    if not rules:
        print("  No firewall rules found for HighTierDashboard")
    else:
        for rule in rules:
            print(f"  Direction: {rule.get('Direction', 'Unknown')}")
            print(f"  Enabled: {rule.get('Enabled', 'Unknown')}")
            print(f"  Action: {rule.get('Action', 'Unknown')}")
            print(f"  Protocol: {rule.get('Protocol', 'Unknown')}")
            print(f"  Local Port: {rule.get('LocalPort', 'Unknown')}")
            print()
    
    # 4. Test local connection
    print("\n4. Testing local connection...")
    if test_local_connection(PORT):
        print(f"  Successfully connected to localhost:{PORT}")
    else:
        print(f"  Could not connect to localhost:{PORT}")
    
    # 5. Get IP addresses
    print("\n5. Available IP addresses:")
    for ip in get_ip_addresses():
        print(f"  http://{ip}:{PORT}")
    
    # 6. Provide recommendations
    print("\nRecommendations:")
    if in_use:
        print("- The port is in use. Try stopping any running instances of the dashboard")
        print("  or change the port number in the configuration.")
    
    if not any(fw_status.values()):
        print("- Windows Firewall appears to be disabled. Consider enabling it")
        print("  and running the firewall setup script again.")
    
    if not rules:
        print("- No firewall rules found. Run the firewall setup script:")
        print("  python -m app.utils.firewall_setup")
    
    if not test_local_connection(PORT):
        print("- Local connection failed. Make sure the dashboard server is running")
        print("  and check the console for any error messages.")

if __name__ == "__main__":
    main() 