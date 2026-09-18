"""Fresh & Shine Cleaning Services backend -- application entry point.

DEMO BUILD: there is no database. There is no SQLite file, no SQLAlchemy, no
migrations and no seed script to run. All data lives in memory in `store.py`
and is reset when the server restarts.

Registers all route blueprints and starts the server.
"""
import os
from datetime import timedelta

from dotenv import load_dotenv
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from routes import admin, auth, bookings, profile, reviews, site, upload
from store import init_store, is_token_blocked

# Load notification config from backend/.env if present (optional).
load_dotenv()

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET", "dev-secret-change-me")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=7)
CORS(app)
jwt = JWTManager(app)


# ---------------------------------------------------------------------------
# JWT blocklist: lets logout invalidate a token server-side.
# In this demo the blocklist is an in-memory set, so it clears on restart.
# ---------------------------------------------------------------------------
@jwt.token_in_blocklist_loader
def _token_in_blocklist(jwt_header, jwt_payload):
    jti = jwt_payload.get("jti")
    return bool(jti) and is_token_blocked(jti)


@jwt.revoked_token_loader
def _revoked_token_callback(jwt_header, jwt_payload):
    return jsonify({"error": "Session has been logged out."}), 401


# Register all route blueprints
for bp in (site.bp, auth.bp, profile.bp, bookings.bp, reviews.bp, admin.bp, upload.bp):
    app.register_blueprint(bp)


# Serve uploaded files statically at /uploads/<filename>.
@app.get("/uploads/<path:filename>")
def serve_upload(filename):
    return send_from_directory(upload.uploads_dir(), filename)


# Seed the demo data once, at startup. No database file is created.
init_store()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
