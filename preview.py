#!/usr/bin/env python3
"""
Local development preview server for Arknights Story Archive
Serves static files from the dist/ directory for development testing
"""

import argparse
import os
import sys
import webbrowser
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler


class PreviewHandler(SimpleHTTPRequestHandler):
    """Custom handler for serving the static site with proper headers"""
    
    def __init__(self, *args, **kwargs):
        """Initialize handler with stable working directory"""
        # Ensure we stay in the correct directory
        try:
            current_dir = os.getcwd()
            if not os.path.exists(current_dir):
                raise FileNotFoundError("Current directory no longer exists")
        except (OSError, FileNotFoundError):
            # If current directory doesn't exist, change to a safe directory
            project_root = Path(__file__).parent
            safe_dir = project_root / 'dist'
            if safe_dir.exists():
                os.chdir(safe_dir)
            else:
                # Fallback to parent directory
                os.chdir(project_root)
        super().__init__(*args, **kwargs)
    
    def end_headers(self):
        # Add CORS headers for development
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def log_error(self, format, *args):
        """Override error logging to handle missing file errors gracefully"""
        if "No such file or directory" in str(args):
            # Don't spam logs with missing file errors
            return
        super().log_error(format, *args)
    
    def translate_path(self, path):
        """Override path translation to handle missing directories gracefully"""
        try:
            return super().translate_path(path)
        except (OSError, FileNotFoundError):
            # If translation fails, return a safe path
            return os.path.join(os.getcwd(), 'index.html')


def check_dist_directory():
    """Check if dist directory exists and has content"""
    dist_path = Path('dist')
    
    if not dist_path.exists():
        print("❌ Error: 'dist' directory not found!")
        print("Please run 'python build.py' first to generate the site.")
        return False
    
    if not any(dist_path.iterdir()):
        print("❌ Error: 'dist' directory is empty!")
        print("Please run 'python build.py' first to generate the site.")
        return False
    
    index_file = dist_path / 'index.html'
    if not index_file.exists():
        print("❌ Warning: 'dist/index.html' not found!")
        print("The site might not have been built correctly.")
        print("Consider running 'python build.py' to rebuild.")
    
    return True


def start_server(port=8000, open_browser=True, host='localhost'):
    """Start the local development server"""
    
    if not check_dist_directory():
        sys.exit(1)
    
    # Get absolute paths to prevent directory issues
    project_root = Path(__file__).parent.absolute()
    dist_path = project_root / 'dist'
    original_cwd = os.getcwd()
    
    # Ensure dist directory still exists
    if not dist_path.exists():
        print("❌ Error: dist directory disappeared!")
        print("Please run 'python build.py' to regenerate the site.")
        sys.exit(1)
    
    server = None
    try:
        os.chdir(dist_path)
        
        # Create server with robust handler
        class RobustPreviewHandler(PreviewHandler):
            def __init__(self, *args, **kwargs):
                self.dist_path = dist_path
                self.project_root = project_root
                self._last_known_good_dir = dist_path
                super().__init__(*args, **kwargs)
            
            def do_GET(self):
                """Override GET handler to ensure we stay in the correct directory"""
                try:
                    # Check if we're in a valid directory
                    current_dir = Path.cwd()
                    if not current_dir.exists():
                        raise FileNotFoundError("Current directory no longer exists")
                    
                    # If not in dist directory, try to change to it
                    if current_dir != self.dist_path:
                        if self.dist_path.exists():
                            os.chdir(self.dist_path)
                            self._last_known_good_dir = self.dist_path
                        else:
                            # Dist doesn't exist, serve from project root
                            os.chdir(self.project_root)
                            self._last_known_good_dir = self.project_root
                            self.send_error(503, "Site needs to be rebuilt. Run 'python build.py'")
                            return
                    
                    super().do_GET()
                    
                except (OSError, FileNotFoundError) as e:
                    # Try to recover to a safe directory
                    try:
                        if self.project_root.exists():
                            os.chdir(self.project_root)
                            self._last_known_good_dir = self.project_root
                        elif self._last_known_good_dir.exists():
                            os.chdir(self._last_known_good_dir)
                        
                        # Send appropriate error response
                        if self.dist_path.exists():
                            self.send_error(404, f"File not found: {self.path}")
                        else:
                            self.send_error(503, "Site needs to be rebuilt. Run 'python build.py'")
                    except Exception:
                        # Last resort error
                        self.send_error(500, "Server in unstable state")
                        
                except Exception as e:
                    # Handle other errors gracefully
                    try:
                        self.send_error(500, f"Server error: {str(e)}")
                    except Exception:
                        # If we can't even send an error, just pass
                        pass
        
        server = HTTPServer((host, port), RobustPreviewHandler)
        server_url = f"http://{host}:{port}"
        
        print("🚀 Starting Arknights Story Archive preview server...")
        print(f"📂 Serving from: {dist_path}")
        print(f"🌐 Server URL: {server_url}")
        print(f"⚡ Server running on port {port}")
        print("\n💡 Tips:")
        print("  - Press Ctrl+C to stop the server")
        print("  - Run 'python build.py' in another terminal to rebuild")
        print("  - Refresh browser to see changes after rebuild")
        print("─" * 50)
        
        # Open browser if requested
        if open_browser:
            print(f"🌍 Opening {server_url} in your default browser...")
            webbrowser.open(server_url)
        
        # Start serving
        server.serve_forever()
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down preview server...")
        if server:
            server.shutdown()
            server.server_close()
        
    except OSError as e:
        if e.errno == 98:  # Address already in use
            print(f"❌ Error: Port {port} is already in use!")
            print(f"Try using a different port: python preview.py --port {port + 1}")
        else:
            print(f"❌ Server error: {e}")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)
        
    finally:
        try:
            if server:
                server.server_close()
        except:
            pass
        try:
            os.chdir(original_cwd)
        except (OSError, FileNotFoundError):
            # If original directory no longer exists, stay where we are
            pass


def main():
    """Main function with command line argument parsing"""
    parser = argparse.ArgumentParser(
        description="Local preview server for Arknights Story Archive",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python preview.py                    # Start on port 8000 and open browser
  python preview.py --port 3000       # Start on port 3000
  python preview.py --no-browser      # Start without opening browser
  python preview.py --host 0.0.0.0    # Allow external connections
        """
    )
    
    parser.add_argument(
        '--port', '-p',
        type=int,
        default=8000,
        help='Port number to serve on (default: 8000)'
    )
    
    parser.add_argument(
        '--host',
        default='localhost',
        help='Host address to bind to (default: localhost)'
    )
    
    parser.add_argument(
        '--no-browser',
        action='store_true',
        help='Don\'t automatically open browser'
    )
    
    args = parser.parse_args()
    
    # Validate port range
    if not (1 <= args.port <= 65535):
        print(f"❌ Error: Port {args.port} is not valid. Use a port between 1-65535.")
        sys.exit(1)
    
    start_server(
        port=args.port,
        open_browser=not args.no_browser,
        host=args.host
    )


if __name__ == '__main__':
    main()