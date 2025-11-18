#!/usr/bin/env python3
"""
Simpel HTTP server til at serve live mandatfordeling HTML.

Kør dette script og åbn http://localhost:8000/live_mandatfordeling.html i din browser.
"""

import http.server
import socketserver
import webbrowser
import threading
import time
from pathlib import Path

PORT = 8000


class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP request handler med CORS support."""

    def end_headers(self):
        # Tilføj CORS headers for at tillade JSON loading
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        return super().end_headers()

    def log_message(self, format, *args):
        # Mindre verbose logging
        if not any(x in args[0] for x in ['.json', '.html']):
            return
        super().log_message(format, *args)


def start_server():
    """Starter HTTP serveren."""
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print(f"Server kører på http://localhost:{PORT}/")
        print(f"Åbn http://localhost:{PORT}/live_mandatfordeling.html i din browser")
        print("\nTryk Ctrl+C for at stoppe serveren")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\nServeren stoppes...")
            httpd.shutdown()


def open_browser():
    """Åbner browseren efter 1 sekund."""
    time.sleep(1)
    webbrowser.open(f'http://localhost:{PORT}/live_mandatfordeling.html')


if __name__ == '__main__':
    # Skift til script directory
    import os
    os.chdir(Path(__file__).parent)

    print("="*70)
    print("LIVE MANDATFORDELING SERVER")
    print("="*70)
    print("\nForbereder server...")

    # Start browser i separat tråd
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()

    # Start server
    start_server()
