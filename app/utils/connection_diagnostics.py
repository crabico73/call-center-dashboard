import socket
import subprocess
import requests
from typing import List, Tuple
import psutil
import netifaces
import time

class ConnectionDiagnostics:
    DEFAULT_PORTS = [8050, 8051, 8052, 8053, 8054]
    
    @staticmethod
    def verify_firewall_rule(rule_name: str = "HighTierDashboard") -> Tuple[bool, str]:
        """Verify if the firewall rule exists and is correctly configured"""
        try:
            result = subprocess.run(
                f'netsh advfirewall firewall show rule name="{rule_name}"',
                shell=True,
                capture_output=True,
                text=True
            )
            
            if "No rules match the specified criteria" in result.stdout:
                return False, "Firewall rule not found"
                
            # Check if rule is properly configured
            output = result.stdout.lower()
            required_settings = [
                ("enabled:", "yes"),
                ("direction:", "in"),
                ("action:", "allow"),
                ("protocol:", "tcp")
            ]
            
            for setting, expected in required_settings:
                if setting not in output or expected not in output:
                    return False, f"Invalid configuration: {setting} should be {expected}"
                    
            return True, "Firewall rule is correctly configured"
            
        except Exception as e:
            return False, f"Error checking firewall rule: {str(e)}"
    
    @staticmethod
    def test_connection(port: int = 8050) -> Tuple[bool, str]:
        """Test if the dashboard is accessible"""
        try:
            # Test localhost
            try:
                response = requests.get(f"http://localhost:{port}", timeout=5)
                if response.status_code == 200:
                    return True, "Connection successful"
            except requests.exceptions.RequestException:
                pass
            
            # Get all IP addresses
            ips = []
            for interface in netifaces.interfaces():
                addrs = netifaces.ifaddresses(interface)
                if netifaces.AF_INET in addrs:
                    for addr in addrs[netifaces.AF_INET]:
                        ips.append(addr['addr'])
            
            # Test each IP
            for ip in ips:
                try:
                    response = requests.get(f"http://{ip}:{port}", timeout=2)
                    if response.status_code == 200:
                        return True, f"Connection successful on {ip}:{port}"
                except requests.exceptions.RequestException:
                    continue
            
            return False, "Could not connect to dashboard"
            
        except Exception as e:
            return False, f"Error testing connection: {str(e)}"
    
    @staticmethod
    def find_available_port(start_port: int = 8050) -> Tuple[int, str]:
        """Find the next available port"""
        for port in range(start_port, start_port + 10):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('', port))
                    return port, f"Port {port} is available"
            except OSError:
                continue
        return -1, "No available ports found in range"
    
    @staticmethod
    def get_process_using_port(port: int) -> Tuple[int, str]:
        """Get information about process using a specific port"""
        for proc in psutil.process_iter(['pid', 'name', 'connections']):
            try:
                for conn in proc.connections():
                    if conn.laddr.port == port:
                        return proc.pid, proc.name()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return -1, ""
    
    def run_diagnostics(self, port: int = 8050) -> List[dict]:
        """Run all diagnostics and return results"""
        results = []
        
        # Check firewall
        fw_success, fw_message = self.verify_firewall_rule()
        results.append({
            "test": "Firewall Rule",
            "status": "Pass" if fw_success else "Fail",
            "message": fw_message
        })
        
        # Check port availability
        if port != 8050:
            port_available, port_message = self.find_available_port(port)
            results.append({
                "test": "Port Availability",
                "status": "Pass" if port_available == port else "Fail",
                "message": port_message
            })
            
            if port_available != port:
                pid, proc_name = self.get_process_using_port(port)
                if pid != -1:
                    results.append({
                        "test": "Port Usage",
                        "status": "Info",
                        "message": f"Port {port} is being used by {proc_name} (PID: {pid})"
                    })
        
        # Test connection
        conn_success, conn_message = self.test_connection(port)
        results.append({
            "test": "Connection Test",
            "status": "Pass" if conn_success else "Fail",
            "message": conn_message
        })
        
        return results

def main():
    """Run diagnostics from command line"""
    diagnostics = ConnectionDiagnostics()
    results = diagnostics.run_diagnostics()
    
    print("\nDiagnostic Results:")
    print("-" * 50)
    for result in results:
        print(f"\n{result['test']}:")
        print(f"Status: {result['status']}")
        print(f"Message: {result['message']}")
    print("\nAvailable IPs for access:")
    for interface in netifaces.interfaces():
        addrs = netifaces.ifaddresses(interface)
        if netifaces.AF_INET in addrs:
            for addr in addrs[netifaces.AF_INET]:
                print(f"http://{addr['addr']}:8050")

if __name__ == "__main__":
    main() 