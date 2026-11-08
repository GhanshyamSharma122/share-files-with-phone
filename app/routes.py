# Flask routes for the Wi-Fi File Share application
import os
import mimetypes
import io
import zipfile

from flask import Blueprint, request, render_template, send_from_directory, send_file, abort, jsonify

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


@main.route("/download-zip", methods=["POST"])
def download_zip():
    """Package selected files into one download for mobile browsers."""
    data = request.get_json(silent=True) or {}
    filenames = data.get("files", [])
    if not isinstance(filenames, list) or not filenames:
        return jsonify({"success": False, "error": "Select at least one file"}), 400

    shared_root = os.path.realpath(SHARED_FOLDER)
    files_to_zip = []
    for filename in filenames:
        if not isinstance(filename, str) or not filename.strip():
            continue
        full_path = os.path.realpath(os.path.join(SHARED_FOLDER, filename))
        if os.path.commonpath([shared_root, full_path]) != shared_root:
            continue
        if os.path.isfile(full_path):
            files_to_zip.append((full_path, os.path.basename(full_path)))

    if not files_to_zip:
        return jsonify({"success": False, "error": "No selected files were found"}), 404

    archive = io.BytesIO()
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as zip_file:
        used_names = set()
        for full_path, filename in files_to_zip:
            archive_name = filename
            suffix = 2
            stem, extension = os.path.splitext(filename)
            while archive_name in used_names:
                archive_name = f"{stem} ({suffix}){extension}"
                suffix += 1
            used_names.add(archive_name)
            zip_file.write(full_path, archive_name)
    archive.seek(0)

    return send_file(
        archive,
        mimetype="application/zip",
        as_attachment=True,
        download_name="wifi-share-files.zip"
    )


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
