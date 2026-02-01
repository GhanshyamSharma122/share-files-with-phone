#!/usr/bin/env python3
"""
Wi-Fi File Share - Share files wirelessly between devices
Run this file to start the server.
"""

from app import create_app
from app.config import HOST, PORT
from app.utils import get_local_ip, SHARED_FOLDER


def main():
    """Start the Wi-Fi File Share server."""
    app = create_app()
    ip = get_local_ip()
    
    print("\n" + "=" * 50)
    print("📡 Wi-Fi File Share Server")
    print("=" * 50)
    print(f"\n📱 Open on phone:  http://{ip}:{PORT}")
    print(f"💻 Local access:   http://localhost:{PORT}")
    print(f"📁 Shared folder:  {SHARED_FOLDER}")
    print("\n(Phone must be connected to your PC hotspot or same Wi-Fi)\n")
    print("=" * 50 + "\n")
    
    app.run(host=HOST, port=PORT, threaded=True)


if __name__ == "__main__":
    main()
