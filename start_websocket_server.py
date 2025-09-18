#!/usr/bin/env python
"""
Script to start the Django ASGI server with WebSocket support
"""
import os
import sys
import subprocess

def main():
    print("Starting Django ASGI server with WebSocket support...")
    print("Server will be available at: http://localhost:8000")
    print("WebSocket endpoint: ws://localhost:8000/ws/chat/room1/")
    print("Press Ctrl+C to stop the server")
    
    # Use subprocess to run daphne with the virtual environment
    try:
        subprocess.run([
            'daphne',
            '--bind', '0.0.0.0',
            '--port', '8000',
            'applaude_api.asgi:application'
        ], check=True)
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()