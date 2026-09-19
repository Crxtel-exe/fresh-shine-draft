"""Upload route: accept multipart image uploads and store them locally.

Files are saved to backend/uploads/ and served back at /uploads/<filename>.
Only image files are accepted, with a size limit (default 5 MB).

This is the one piece of state a demo build still writes to disk -- the image
files themselves. There is still no database.
"""
import os
import uuid

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

bp = Blueprint("upload", __name__, url_prefix="/api")

# Allowed image content types and their file extensions.
ALLOWED_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/gif": ".gif",
    "image/webp": ".webp",
    "image/svg+xml": ".svg",
    "image/bmp": ".bmp",
}

MAX_SIZE = 5 * 1024 * 1024  # 5 MB


def uploads_dir():
    """Absolute path to the uploads folder (backend/uploads/)."""
    return os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads"
    )


@bp.post("/upload")
@jwt_required()
def upload_file():
    """Save an uploaded image and return its public URL.

    Expects a multipart/form-data request with a file field named `file`.
    Returns {"url": "/uploads/<filename>"} on success.
    """
    if "file" not in request.files:
        return jsonify({"error": "No file provided."}), 400

    file = request.files["file"]
    if not file or not file.filename:
        return jsonify({"error": "No file provided."}), 400

    content_type = (file.mimetype or "").lower()
    if content_type not in ALLOWED_TYPES:
        return jsonify({"error": "Only image files are allowed (JPG, PNG, GIF, WEBP, SVG, BMP)."}), 400

    # Reject empty files and enforce the size limit.
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    if size == 0:
        return jsonify({"error": "The uploaded file is empty."}), 400
    if size > MAX_SIZE:
        return jsonify({"error": "Image is too large. Maximum size is 5 MB."}), 400

    # Generate a unique filename while keeping the original extension.
    ext = ALLOWED_TYPES[content_type]
    filename = f"{uuid.uuid4().hex}{ext}"

    directory = uploads_dir()
    os.makedirs(directory, exist_ok=True)
    file.save(os.path.join(directory, filename))

    return jsonify({"url": f"/uploads/{filename}"}), 201
