from http.server import HTTPServer, SimpleHTTPRequestHandler
import socket
import webbrowser
from threading import Timer
import os
import sys

# Disable proxy settings for this script
os.environ['NO_PROXY'] = 'localhost,127.0.0.1'
if 'HTTP_PROXY' in os.environ:
    del os.environ['HTTP_PROXY']
if 'HTTPS_PROXY' in os.environ:
    del os.environ['HTTPS_PROXY']

class NoAuthHandler(SimpleHTTPRequestHandler):
    """Custom handler that allows all requests without authentication"""
    
    def do_GET(self):
        try:
            # Add CORS headers
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'X-Requested-With')
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            # Serve index.html for root path
            if self.path == '/':
                try:
                    with open('index.html', 'rb') as file:
                        self.wfile.write(file.read())
                except FileNotFoundError:
                    print("Error: index.html not found in current directory")
                    print(f"Current directory: {os.getcwd()}")
                    print("Files in current directory:")
                    print('\n'.join(os.listdir('.')))
                    raise
            else:
                # For other paths, use the default behavior
                super().do_GET()
        except Exception as e:
            print(f"Error handling GET request: {e}")
            raise

    def do_OPTIONS(self):
        # Handle OPTIONS request for CORS
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'X-Requested-With')
        self.end_headers()

def test_port(port):
    """Test if port is available"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', port))
            return True
    except OSError:
        return False

def find_free_port(start_port=8050):
    """Find next available port"""
    port = start_port
    while not test_port(port) and port < start_port + 10:
        port += 1
    return port if port < start_port + 10 else None

def run_server():
    """Run a simple HTTP server"""
    PORT = 8050
    
    # Find available port
    if not test_port(PORT):
        print(f"\nPort {PORT} is in use.")
        PORT = find_free_port()
        if not PORT:
            print("Error: Could not find an available port")
            sys.exit(1)
        print(f"Using alternative port: {PORT}")
    
    try:
        # Bind to all interfaces
        server_address = ('0.0.0.0', PORT)
        httpd = HTTPServer(server_address, NoAuthHandler)
        
        print("\nTest Server Running!")
        print("-" * 50)
        print("Available URLs:")
        print(f"→ http://localhost:{PORT}")
        print(f"→ http://127.0.0.1:{PORT}")
        
        # Get all IP addresses
        hostname = socket.gethostname()
        try:
            host_ip = socket.gethostbyname(hostname)
            print(f"→ http://{host_ip}:{PORT}")
        except:
            pass
            
        print("\nPress Ctrl+C to stop the server")
        print("\nChecking server accessibility...")
        
        def test_connection():
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1)
                    s.connect(('127.0.0.1', PORT))
                print("✓ Server is accessible locally")
                webbrowser.open(f'http://localhost:{PORT}')
            except Exception as e:
                print(f"✗ Could not connect to server: {e}")
        
        Timer(1.5, test_connection).start()
        httpd.serve_forever()
        
    except Exception as e:
        print(f"\nError starting server: {e}")
        print("\nTroubleshooting steps:")
        print("1. Check if another program is using port", PORT)
        print("2. Try running as administrator")
        print("3. Check firewall settings")
        print("4. Verify network adapter settings")
        sys.exit(1)

if __name__ == '__main__':
    try:
        run_server()
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1) 