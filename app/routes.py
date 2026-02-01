# Flask routes for the Wi-Fi File Share application
import os
import mimetypes

from flask import Blueprint, request, render_template, send_from_directory, abort, jsonify

from app.config import SHARED_FOLDER, PORT
from app.utils import (
    get_local_ip, generate_qr_code, list_shared_files, 
    get_storage_stats, sanitize_filename
)

# Create blueprint
main = Blueprint('main', __name__)


@main.route("/")
def index():
    """Render the main page."""
    ip = get_local_ip()
    url = f"http://{ip}:{PORT}"
    qr_code = generate_qr_code(url)
    stats = get_storage_stats()
    return render_template(
        "index.html", 
        files=list_shared_files(), 
        ip=ip, 
        port=PORT,
        qr_code=qr_code, 
        stats=stats
    )


@main.route("/upload", methods=["POST"])
def upload_files():
    """Handle file uploads."""
    uploaded = 0
    for file in request.files.getlist("files"):
        if file.filename.strip():
            safe_name = sanitize_filename(file.filename)
            file.save(os.path.join(SHARED_FOLDER, safe_name))
            uploaded += 1
    return jsonify({"success": True, "uploaded": uploaded})


@main.route("/download/<path:filename>")
def download(filename):
    """Download a file."""
    full_path = os.path.abspath(os.path.join(SHARED_FOLDER, filename))
    if not full_path.startswith(os.path.abspath(SHARED_FOLDER)):
        abort(403)
    if not os.path.exists(full_path):
        abort(404)
    return send_from_directory(SHARED_FOLDER, filename, as_attachment=True)


@main.route("/stream/<path:filename>")
def stream_file(filename):
    """Stream a file for preview."""
    full_path = os.path.abspath(os.path.join(SHARED_FOLDER, filename))
    if not full_path.startswith(os.path.abspath(SHARED_FOLDER)):
        abort(403)
    if not os.path.exists(full_path):
        abort(404)
    
    mimetype = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
    return send_from_directory(SHARED_FOLDER, filename, mimetype=mimetype)


@main.route("/delete/<path:filename>", methods=["DELETE"])
def delete_file(filename):
    """Delete a file."""
    full_path = os.path.abspath(os.path.join(SHARED_FOLDER, filename))
    if not full_path.startswith(os.path.abspath(SHARED_FOLDER)):
        return jsonify({"success": False, "error": "Access denied"}), 403
    if not os.path.exists(full_path):
        return jsonify({"success": False, "error": "File not found"}), 404
    
    try:
        os.remove(full_path)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@main.route("/rename", methods=["POST"])
def rename_file():
    """Rename a file."""
    data = request.json
    old_name = data.get("old_name", "").strip()
    new_name = data.get("new_name", "").strip()
    
    if not old_name or not new_name:
        return jsonify({"success": False, "error": "Invalid names"}), 400
    
    old_path = os.path.abspath(os.path.join(SHARED_FOLDER, old_name))
    new_path = os.path.abspath(os.path.join(SHARED_FOLDER, sanitize_filename(new_name)))
    
    if not old_path.startswith(os.path.abspath(SHARED_FOLDER)):
        return jsonify({"success": False, "error": "Access denied"}), 403
    if not os.path.exists(old_path):
        return jsonify({"success": False, "error": "File not found"}), 404
    if os.path.exists(new_path):
        return jsonify({"success": False, "error": "A file with that name already exists"}), 400
    
    try:
        os.rename(old_path, new_path)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@main.route("/stats")
def get_stats():
    """Get storage statistics."""
    return jsonify(get_storage_stats())
