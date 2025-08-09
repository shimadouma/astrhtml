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
    
    def end_headers(self):
        # Add CORS headers for development
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()


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
    
    # Change to dist directory
    dist_path = Path('dist').absolute()
    original_cwd = os.getcwd()
    
    try:
        os.chdir(dist_path)
        
        # Start server with PreviewHandler
        server = HTTPServer((host, port), PreviewHandler)
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
        server.shutdown()
        
    except OSError as e:
        if e.errno == 98:  # Address already in use
            print(f"❌ Error: Port {port} is already in use!")
            print(f"Try using a different port: python preview.py --port {port + 1}")
        else:
            print(f"❌ Server error: {e}")
        sys.exit(1)
        
    finally:
        os.chdir(original_cwd)


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