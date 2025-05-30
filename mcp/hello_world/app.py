#!/usr/bin/env python3
import http.server
import socketserver

PORT = 8080

class MCPHelloWorldHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Always return Hello World response
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Hello World from MCP Server!")

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), MCPHelloWorldHandler) as httpd:
        print(f"Hello World MCP Server running at http://localhost:{PORT}")
        httpd.serve_forever()
