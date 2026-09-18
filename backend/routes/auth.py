"""Authentication routes: signup, login, me, forgot/reset password.

All accounts live in the in-memory store -- no database is involved.
"""
import secrets
from datetime import datetime, timedelta

from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt, get_jwt_identity, jwt_required

import store
from helpers import (
    EMAIL_RE,
    PHONE_RE,
    check_password,
    hash_password,
    public_user,
    valid_pampanga,
)

bp = Blueprint("auth", __name__, url_prefix="/api/auth")


def _email_taken(email):
    return any((u["email"] or "").lower() == email for u in store.list_users())


def _phone_taken(phone):
    return any((u["phone"] or "") == phone for u in store.list_users())


@bp.post("/signup")
def signup():
    data = request.get_json(silent=True) or {}
    first = (data.get("first_name") or "").strip()
    last = (data.get("last_name") or "").strip()
    phone = (data.get("phone") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    confirm = data.get("confirm_password") or ""
    municipality = (data.get("municipality") or "").strip()
    barangay = (data.get("barangay") or "").strip()
    terms = data.get("terms")

    if not all([first, last, phone, email, password, municipality, barangay]):
        return jsonify({"error": "All fields are required."}), 400
    if not EMAIL_RE.match(email):
        return jsonify({"error": "Please enter a valid email address."}), 400
    if not PHONE_RE.match(phone):
        return jsonify({"error": "Please enter a valid Philippine mobile number (e.g. 09171234567)."}), 400
    if len(password) < store.PASSWORD_MIN_LENGTH:
        return jsonify({"error": "Password must be at least 6 characters."}), 400
    if password != confirm:
        return jsonify({"error": "Passwords do not match."}), 400
    if not terms:
        return jsonify({"error": "You must accept the terms and conditions."}), 400
    if not valid_pampanga(municipality, barangay):
        return jsonify({"error": "Please choose a valid Pampanga location."}), 400

    if _email_taken(email):
        return jsonify({"error": "An account with this email already exists."}), 409
    if _phone_taken(phone):
        return jsonify({"error": "An account with this phone number already exists."}), 409

    user = store.create_user(
        {
            "first_name": first,
            "last_name": last,
            "phone": phone,
            "email": email,
            "password_hash": hash_password(password),
            "role": "user",
            "municipality": municipality,
            "barangay": barangay,
        }
    )
    return jsonify({"token": create_access_token(identity=str(user["id"])), "user": public_user(user)}), 201


@bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    identifier = (data.get("identifier") or "").strip().lower()
    password = data.get("password") or ""

    if not identifier or not password:
        return jsonify({"error": "Email/phone and password are required."}), 400

    user = store.find_user(identifier)
    if not user or not check_password(password, user["password_hash"]):
        return jsonify({"error": "Invalid credentials."}), 401

    return jsonify({"token": create_access_token(identity=str(user["id"])), "user": public_user(user)})


@bp.get("/me")
@jwt_required()
def me():
    user = store.get_user(get_jwt_identity())
    if not user:
        return jsonify({"error": "User not found."}), 404
    return jsonify({"user": public_user(user)})


@bp.post("/logout")
@jwt_required()
def logout():
    """Invalidate the current user token so it can no longer be used."""
    store.block_token(get_jwt()["jti"])
    return jsonify({"message": "Logged out successfully."})


@bp.post("/forgot")
def forgot():
    data = request.get_json(silent=True) or {}
    identifier = (data.get("identifier") or "").strip().lower()
    user = store.find_user(identifier)
    if not user:
        # Do not reveal whether the account exists
        return jsonify({"message": "If that account exists, a reset link has been generated."})

    token = secrets.token_urlsafe(32)
    expires = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
    store.create_password_reset(user["id"], token, expires)
    # In a real app you would email/SMS this link. For this demo we return it.
    return jsonify(
        {
            "message": "If that account exists, a reset link has been sent.",
            "reset_token": token,  # demo convenience
        }
    )


@bp.post("/reset-password")
def reset_password():
    data = request.get_json(silent=True) or {}
    token = (data.get("token") or "").strip()
    new_password = data.get("password") or ""
    if len(new_password) < store.PASSWORD_MIN_LENGTH:
        return jsonify({"error": "Password must be at least 6 characters."}), 400

    row = store.find_password_reset(token)
    if not row:
        return jsonify({"error": "Invalid or expired reset token."}), 400
    if datetime.now().strftime("%Y-%m-%d %H:%M:%S") > row["expires_at"]:
        return jsonify({"error": "Reset token has expired."}), 400

    store.update_user(row["user_id"], {"password_hash": hash_password(new_password)})
    store.mark_password_reset_used(row["id"])
    return jsonify({"message": "Password has been reset. You can now log in."})
