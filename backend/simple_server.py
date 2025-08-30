
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from main import app
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=False)
except ImportError:
    # Fallback to minimal server
    from http.server import HTTPServer, SimpleHTTPRequestHandler
    import json
    
    class SAAHandler(SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path == "/health":
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                response = {"status": "healthy", "mode": "fallback"}
                self.wfile.write(json.dumps(response).encode())
            else:
                super().do_GET()
    
    with HTTPServer(("", 8001), SAAHandler) as httpd:
        print(f"Fallback server running on port 8001")
        httpd.serve_forever()
