import subprocess
import sys
import time

def run_as_admin():
    """Check if running with admin privileges"""
    try:
        return subprocess.run('net session', capture_output=True, shell=True).returncode == 0
    except:
        return False

def check_existing_rule(rule_name="HighTierDashboard"):
    """Check if firewall rule already exists"""
    try:
        result = subprocess.run(
            f'netsh advfirewall firewall show rule name="{rule_name}"',
            shell=True,
            capture_output=True,
            text=True
        )
        return "No rules match the specified criteria" not in result.stdout
    except Exception as e:
        print(f"Error checking firewall rule: {e}")
        return False

def delete_existing_rule(rule_name="HighTierDashboard"):
    """Delete existing firewall rule if it exists"""
    try:
        if check_existing_rule(rule_name):
            subprocess.run(
                f'netsh advfirewall firewall delete rule name="{rule_name}"',
                shell=True,
                check=True
            )
            print(f"Deleted existing rule: {rule_name}")
            time.sleep(1)  # Give Windows time to process
    except Exception as e:
        print(f"Error deleting rule: {e}")

def create_firewall_rule(port=8050, rule_name="HighTierDashboard"):
    """Create new firewall rules for inbound and outbound traffic"""
    try:
        # Create inbound rule
        inbound_command = (
            f'netsh advfirewall firewall add rule '
            f'name="{rule_name}" '
            f'dir=in '
            f'action=allow '
            f'protocol=TCP '
            f'localport={port} '
            f'enable=yes '
            f'profile=any '
            f'description="Allow inbound traffic for Call Center Dashboard"'
        )
        
        # Create outbound rule
        outbound_command = (
            f'netsh advfirewall firewall add rule '
            f'name="{rule_name}" '
            f'dir=out '
            f'action=allow '
            f'protocol=TCP '
            f'localport={port} '
            f'enable=yes '
            f'profile=any '
            f'description="Allow outbound traffic for Call Center Dashboard"'
        )
        
        # Execute commands
        subprocess.run(inbound_command, shell=True, check=True)
        print(f"Created inbound rule for port {port}")
        
        subprocess.run(outbound_command, shell=True, check=True)
        print(f"Created outbound rule for port {port}")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error creating firewall rules: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

def verify_firewall_rules(port=8050, rule_name="HighTierDashboard"):
    """Verify that firewall rules are correctly configured"""
    try:
        result = subprocess.run(
            f'netsh advfirewall firewall show rule name="{rule_name}"',
            shell=True,
            capture_output=True,
            text=True
        )
        
        if "No rules match the specified criteria" in result.stdout:
            print("Error: Firewall rules not found")
            return False
            
        output = result.stdout.lower()
        
        # Check required settings
        checks = {
            "enabled": "enabled:                              yes",
            "protocol": f"protocol:                             tcp",
            "port": f"localport:                            {port}",
            "action": "action:                               allow"
        }
        
        for key, value in checks.items():
            if value.lower() not in output:
                print(f"Error: Invalid {key} configuration")
                print(f"Expected: {value}")
                return False
        
        print("Firewall rules verified successfully!")
        return True
        
    except Exception as e:
        print(f"Error verifying firewall rules: {e}")
        return False

def main():
    """Main function to set up firewall rules"""
    if not run_as_admin():
        print("Error: This script must be run with administrator privileges")
        print("Please right-click on PowerShell/Command Prompt and select 'Run as administrator'")
        return False
        
    print("\nCall Center Dashboard - Firewall Setup")
    print("-" * 50)
    
    # Configuration
    PORT = 8050
    RULE_NAME = "HighTierDashboard"
    
    print(f"\nConfiguring firewall for port {PORT}...")
    
    # Delete existing rules
    delete_existing_rule(RULE_NAME)
    
    # Create new rules
    if create_firewall_rule(PORT, RULE_NAME):
        print("\nFirewall rules created successfully!")
    else:
        print("\nError: Failed to create firewall rules")
        return False
    
    # Verify rules
    print("\nVerifying firewall configuration...")
    if verify_firewall_rules(PORT, RULE_NAME):
        print("\nFirewall setup completed successfully!")
        print(f"The dashboard should now be accessible on port {PORT}")
        print("\nYou can access the dashboard using:")
        print(f"- http://localhost:{PORT}")
        print("- http://<your-ip-address>:8050")
    else:
        print("\nError: Firewall verification failed")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 