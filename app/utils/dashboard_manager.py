import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import os
import threading
import webbrowser
from typing import Optional
from app.services.high_tier_analytics import HighTierAnalyticsService
from app.components.high_tier_dashboard import HighTierDashboard

class DashboardManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Dashboard Manager")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        # Style configuration
        style = ttk.Style()
        style.configure('Success.TButton', background='green')
        style.configure('Danger.TButton', background='red')
        
        # Variables
        self.port = tk.StringVar(value="8050")
        self.rule_name = tk.StringVar(value="HighTierDashboard")
        self.server_status = tk.StringVar(value="Stopped")
        self.firewall_status = tk.StringVar(value="Not Configured")
        
        # Server instance
        self.dashboard: Optional[HighTierDashboard] = None
        self.server_thread: Optional[threading.Thread] = None
        
        self._create_gui()
        self._check_firewall_status()
        
    def _create_gui(self):
        """Create the GUI elements"""
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Server Configuration Section
        server_frame = ttk.LabelFrame(main_frame, text="Server Configuration", padding="10")
        server_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(server_frame, text="Port:").grid(row=0, column=0, padx=5, pady=5)
        ttk.Entry(server_frame, textvariable=self.port).grid(row=0, column=1, padx=5, pady=5)
        
        # Status Section
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(status_frame, text="Server Status:").grid(row=0, column=0, padx=5, pady=5)
        ttk.Label(status_frame, textvariable=self.server_status).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(status_frame, text="Firewall Status:").grid(row=1, column=0, padx=5, pady=5)
        ttk.Label(status_frame, textvariable=self.firewall_status).grid(row=1, column=1, padx=5, pady=5)
        
        # Actions Section
        actions_frame = ttk.LabelFrame(main_frame, text="Actions", padding="10")
        actions_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Server controls
        server_controls = ttk.Frame(actions_frame)
        server_controls.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(
            server_controls,
            text="Start Server",
            command=self.start_server
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            server_controls,
            text="Stop Server",
            command=self.stop_server
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            server_controls,
            text="Open Dashboard",
            command=self.open_dashboard
        ).pack(side=tk.LEFT, padx=5)
        
        # Firewall controls
        firewall_controls = ttk.Frame(actions_frame)
        firewall_controls.pack(fill=tk.X)
        
        ttk.Button(
            firewall_controls,
            text="Configure Firewall",
            command=self.configure_firewall
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            firewall_controls,
            text="Remove Firewall Rule",
            command=self.remove_firewall_rule
        ).pack(side=tk.LEFT, padx=5)
        
        # Log Section
        log_frame = ttk.LabelFrame(main_frame, text="Log", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = tk.Text(log_frame, height=10, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Add scrollbar to log
        scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        
    def log(self, message: str):
        """Add message to log"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        
    def start_server(self):
        """Start the dashboard server"""
        if self.server_thread and self.server_thread.is_alive():
            self.log("Server is already running")
            return
            
        try:
            port = int(self.port.get())
            
            # Initialize services
            analytics_service = HighTierAnalyticsService()
            self.dashboard = HighTierDashboard(analytics_service)
            
            # Start server in a separate thread
            self.server_thread = threading.Thread(
                target=self._run_server,
                args=(port,),
                daemon=True
            )
            self.server_thread.start()
            
            self.server_status.set("Running")
            self.log(f"Server started on port {port}")
            
        except ValueError:
            messagebox.showerror("Error", "Invalid port number")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start server: {str(e)}")
            
    def stop_server(self):
        """Stop the dashboard server"""
        if not self.server_thread or not self.server_thread.is_alive():
            self.log("Server is not running")
            return
            
        try:
            if self.dashboard:
                self.dashboard.app.server.shutdown()
            self.server_status.set("Stopped")
            self.log("Server stopped")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to stop server: {str(e)}")
            
    def _run_server(self, port: int):
        """Run the dashboard server"""
        try:
            self.dashboard.run_server(port=port)
        except Exception as e:
            self.log(f"Server error: {str(e)}")
            self.server_status.set("Error")
            
    def configure_firewall(self):
        """Configure Windows Firewall"""
        try:
            port = int(self.port.get())
            rule_name = self.rule_name.get()
            
            # Remove existing rule
            subprocess.run(
                f'netsh advfirewall firewall delete rule name="{rule_name}"',
                shell=True,
                capture_output=True
            )
            
            # Add new rules
            inbound_command = (
                f'netsh advfirewall firewall add rule '
                f'name="{rule_name}" '
                f'dir=in '
                f'action=allow '
                f'protocol=TCP '
                f'localport={port}'
            )
            
            outbound_command = (
                f'netsh advfirewall firewall add rule '
                f'name="{rule_name}" '
                f'dir=out '
                f'action=allow '
                f'protocol=TCP '
                f'localport={port}'
            )
            
            subprocess.run(inbound_command, shell=True, check=True)
            subprocess.run(outbound_command, shell=True, check=True)
            
            self.firewall_status.set("Configured")
            self.log(f"Firewall configured for port {port}")
            
        except subprocess.CalledProcessError as e:
            messagebox.showerror(
                "Error",
                "Failed to configure firewall. Try running as administrator."
            )
            self.log(f"Firewall error: {str(e)}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error: {str(e)}")
            self.log(f"Error: {str(e)}")
            
    def remove_firewall_rule(self):
        """Remove firewall rule"""
        try:
            rule_name = self.rule_name.get()
            
            subprocess.run(
                f'netsh advfirewall firewall delete rule name="{rule_name}"',
                shell=True,
                check=True
            )
            
            self.firewall_status.set("Not Configured")
            self.log("Firewall rule removed")
            
        except subprocess.CalledProcessError as e:
            messagebox.showerror(
                "Error",
                "Failed to remove firewall rule. Try running as administrator."
            )
            self.log(f"Firewall error: {str(e)}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error: {str(e)}")
            self.log(f"Error: {str(e)}")
            
    def _check_firewall_status(self):
        """Check current firewall rule status"""
        try:
            rule_name = self.rule_name.get()
            result = subprocess.run(
                f'netsh advfirewall firewall show rule name="{rule_name}"',
                shell=True,
                capture_output=True,
                text=True
            )
            
            if "No rules match the specified criteria" in result.stdout:
                self.firewall_status.set("Not Configured")
            else:
                self.firewall_status.set("Configured")
                
        except Exception:
            self.firewall_status.set("Unknown")
            
    def open_dashboard(self):
        """Open dashboard in default browser"""
        if self.server_thread and self.server_thread.is_alive():
            port = self.port.get()
            webbrowser.open(f"http://localhost:{port}")
        else:
            messagebox.showwarning("Warning", "Server is not running")
            
    def run(self):
        """Start the GUI"""
        self.root.mainloop()

def main():
    manager = DashboardManager()
    manager.run()

if __name__ == "__main__":
    main() 