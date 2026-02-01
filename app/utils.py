# Utility functions for the Wi-Fi File Share application
import os
import io
import base64
import socket
import datetime

from app.config import (
    SHARED_FOLDER, FILE_CATEGORIES, FILE_ICONS, PREVIEWABLE_EXTENSIONS
)

# Re-export for convenience
SHARED_FOLDER = SHARED_FOLDER


def get_local_ip():
    """Get the local network IP address."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()


def generate_qr_code(url):
    """Generate a QR code as base64 encoded PNG."""
    try:
        import qrcode
        qr = qrcode.QRCode(version=1, box_size=6, border=2)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="#a855f7", back_color="#1e1b4b")
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        return base64.b64encode(buffer.getvalue()).decode()
    except ImportError:
        return None


def get_file_icon(filename):
    """Get an emoji icon for a file based on its extension."""
    ext = os.path.splitext(filename)[1].lower()
    return FILE_ICONS.get(ext, '📁')


def get_file_category(filename):
    """Get the category of a file based on its extension."""
    ext = os.path.splitext(filename)[1].lower()
    for cat, exts in FILE_CATEGORIES.items():
        if ext in exts:
            return cat
    return 'other'


def format_size(size_bytes):
    """Format file size in human-readable format."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


def is_previewable(filename):
    """Check if a file can be previewed in the browser."""
    ext = os.path.splitext(filename)[1].lower()
    return ext in PREVIEWABLE_EXTENSIONS


def list_shared_files():
    """List all files in the shared folder with metadata."""
    files = []
    for filename in os.listdir(SHARED_FOLDER):
        path = os.path.join(SHARED_FOLDER, filename)
        if os.path.isfile(path):
            size_bytes = os.path.getsize(path)
            modified = datetime.datetime.fromtimestamp(os.path.getmtime(path))
            files.append({
                "name": filename,
                "size": format_size(size_bytes),
                "size_bytes": size_bytes,
                "mtime": modified.strftime("%Y-%m-%d %H:%M"),
                "mtime_ts": os.path.getmtime(path),
                "icon": get_file_icon(filename),
                "category": get_file_category(filename),
                "previewable": is_previewable(filename)
            })
    return sorted(files, key=lambda x: x["mtime_ts"], reverse=True)


def get_storage_stats():
    """Get storage statistics for the shared folder."""
    files = list_shared_files()
    total_size = sum(f["size_bytes"] for f in files)
    categories = {}
    
    for f in files:
        cat = f["category"]
        if cat not in categories:
            categories[cat] = {"count": 0, "size": 0}
        categories[cat]["count"] += 1
        categories[cat]["size"] += f["size_bytes"]
    
    for cat in categories:
        categories[cat]["size_formatted"] = format_size(categories[cat]["size"])
    
    return {
        "total_files": len(files),
        "total_size": format_size(total_size),
        "total_size_bytes": total_size,
        "categories": categories
    }


def sanitize_filename(filename):
    """Sanitize a filename to prevent path traversal attacks."""
    return filename.replace("/", "_").replace("\\", "_")
