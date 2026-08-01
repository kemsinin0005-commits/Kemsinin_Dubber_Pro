import http.server
import socketserver
import os
import sys

PORT = 8000

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Allow CORS and prevent caching for active development
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        super().end_headers()

Handler = CustomHTTPRequestHandler
Handler.extensions_map.update({
    '.js': 'application/javascript',
    '.css': 'text/css',
    '.srt': 'text/plain',
})

print(f"\n=======================================================")
print(f"Starting Kemsinin Dubber Pro Studio locally...")
print(f"👉 http://localhost:{PORT}")
print("Press Ctrl+C to stop the server.")
print(f"=======================================================\n")

try:
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        httpd.serve_forever()
except KeyboardInterrupt:
    print("\nServer stopped.")
    sys.exit(0)
except Exception as e:
    print(f"Error starting server: {e}")
