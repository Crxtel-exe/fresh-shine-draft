"""Profile routes: update info and change password.

DEMO BUILD: profile changes live in memory and reset when the server restarts.
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

import store
from helpers import EMAIL_RE, PHONE_RE, check_password, hash_password, public_user

bp = Blueprint("profile", __name__, url_prefix="/api/profile")


@bp.put("")
@jwt_required()
def update_profile():
    uid = get_jwt_identity()
    data = request.get_json(silent=True) or {}
    user = store.get_user(uid)
    if not user:
        return jsonify({"error": "User not found."}), 404

    first = (data.get("first_name") or user["first_name"]).strip()
    last = (data.get("last_name") or user["last_name"]).strip()
    phone = (data.get("phone") or user["phone"]).strip()
    email = (data.get("email") or user["email"]).strip().lower()
    municipality = data.get("municipality") or user["municipality"]
    barangay = data.get("barangay") or user["barangay"]
    address = data.get("address") or user["address"]
    profile_pic = data.get("profile_pic") or user["profile_pic"]

    if not EMAIL_RE.match(email):
        return jsonify({"error": "Please enter a valid email address."}), 400
    if not PHONE_RE.match(phone):
        return jsonify({"error": "Please enter a valid Philippine phone number."}), 400

    for other in store.list_users():
        if other["id"] == user["id"]:
            continue
        if (other["email"] or "").lower() == email or (other["phone"] or "") == phone:
            return jsonify({"error": "Email or phone is already in use."}), 409

    updated = store.update_user(
        uid,
        {
            "first_name": first,
            "last_name": last,
            "phone": phone,
            "email": email,
            "municipality": municipality,
            "barangay": barangay,
            "address": address,
            "profile_pic": profile_pic,
        },
    )
    return jsonify({"user": public_user(updated)})


@bp.put("/password")
@jwt_required()
def change_password():
    uid = get_jwt_identity()
    data = request.get_json(silent=True) or {}
    current = data.get("current_password") or ""
    new_password = data.get("new_password") or ""

    user = store.get_user(uid)
    if not user or not check_password(current, user["password_hash"]):
        return jsonify({"error": "Current password is incorrect."}), 400
    if len(new_password) < store.PASSWORD_MIN_LENGTH:
        return jsonify({"error": "New password must be at least 6 characters."}), 400

    store.update_user(uid, {"password_hash": hash_password(new_password)})
    return jsonify({"message": "Password updated successfully."})
