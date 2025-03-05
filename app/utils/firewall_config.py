import subprocess
import sys
import os

def configure_firewall(port: int = 8050, rule_name: str = "HighTierDashboard") -> bool:
    """
    Configure Windows Firewall to allow dashboard access
    
    Args:
        port: The port number to open (default: 8050)
        rule_name: Name of the firewall rule (default: HighTierDashboard)
    
    Returns:
        bool: True if configuration was successful, False otherwise
    """
    try:
        # Remove existing rule if it exists
        subprocess.run(
            f'netsh advfirewall firewall delete rule name="{rule_name}"',
            shell=True,
            capture_output=True
        )
        
        # Add new inbound rule
        inbound_command = (
            f'netsh advfirewall firewall add rule '
            f'name="{rule_name}" '
            f'dir=in '
            f'action=allow '
            f'protocol=TCP '
            f'localport={port}'
        )
        
        # Add new outbound rule
        outbound_command = (
            f'netsh advfirewall firewall add rule '
            f'name="{rule_name}" '
            f'dir=out '
            f'action=allow '
            f'protocol=TCP '
            f'localport={port}'
        )
        
        # Execute commands
        subprocess.run(inbound_command, shell=True, check=True)
        subprocess.run(outbound_command, shell=True, check=True)
        
        print(f"✅ Firewall configured successfully for port {port}")
        print(f"You can now access the dashboard at: http://localhost:{port}")
        print("\nTo remove this rule later, run:")
        print(f'netsh advfirewall firewall delete rule name="{rule_name}"')
        
        return True
        
    except subprocess.CalledProcessError as e:
        print("❌ Error configuring firewall. Try running as administrator.")
        print(f"Error details: {str(e)}")
        return False
    
    except Exception as e:
        print("❌ Unexpected error configuring firewall")
        print(f"Error details: {str(e)}")
        return False

if __name__ == "__main__":
    # If run directly, configure firewall with default settings
    configure_firewall() 