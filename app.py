import os
import sys
import subprocess
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler

# ============ CONFIGURATION ============
BOT_FILE = "main.py"  # Your bot file name
PORT = 50000
HOST = "0.0.0.0"

# ============ WEB SERVER ============

class SimpleHandler(BaseHTTPRequestHandler):
    """Simple web server to show bot status"""
    
    def log_message(self, format, *args):
        pass  # Suppress logging
    
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(f"✅ P4ON BOT IS RUNNING!\n📁 File: {BOT_FILE}\n🌐 Port: {PORT}\n".encode())

def start_server():
    """Start simple web server"""
    server = HTTPServer((HOST, PORT), SimpleHandler)
    print(f"🌐 Web server running on http://{HOST}:{PORT}")
    server.serve_forever()

# ============ BOT RUNNER ============

def run_bot():
    """Run the bot"""
    print(f"🤖 Starting bot: {BOT_FILE}")
    
    # Check if bot file exists
    if not os.path.exists(BOT_FILE):
        print(f"❌ Error: {BOT_FILE} not found!")
        sys.exit(1)
    
    # Run the bot
    try:
        subprocess.run([sys.executable, BOT_FILE], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped")
    except Exception as e:
        print(f"❌ Error: {e}")

# ============ MAIN ============

def main():
    print("=" * 50)
    print("🚀 P4ON BOT RUNNER")
    print("=" * 50)
    print(f"📁 Bot File: {BOT_FILE}")
    print(f"🌐 Server: http://{HOST}:{PORT}")
    print("=" * 50)
    print("")
    
    # Start web server in background
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Run the bot
    run_bot()

if __name__ == "__main__":
    main()
