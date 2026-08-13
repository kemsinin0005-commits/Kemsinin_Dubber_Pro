import http.server
import socketserver
import os
import sys

PORT = 8000

import urllib.request
import urllib.parse

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/tts?text="):
            query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            text = query.get('text', [''])[0]
            if text:
                tts_url = f"https://translate.google.com/translate_tts?ie=UTF-8&tl=km&client=tw-ob&q={urllib.parse.quote(text)}"
                try:
                    req = urllib.request.Request(tts_url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req) as response:
                        self.send_response(200)
                        self.send_header('Content-type', 'audio/mpeg')
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
                        self.end_headers()
                        self.wfile.write(response.read())
                        return
                except Exception as e:
                    self.send_response(500)
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(str(e).encode())
                    return
        super().do_GET()

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

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

print(f"\n=======================================================")
print(f"Starting Kemsinin Dubber Pro Studio locally...")
print(f" -> http://localhost:{PORT}")
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
