"""Review routes: public list, create (one per completed booking).

DEMO BUILD: reviews are held in memory and reset when the server restarts.
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

import store
from helpers import review_dict

bp = Blueprint("reviews", __name__, url_prefix="/api/reviews")


@bp.get("")
def public_reviews():
    rows = store.list_reviews(with_user=True)
    return jsonify(
        {"reviews": [{**review_dict(r), "user_name": r["user_name"]} for r in rows]}
    )


@bp.post("")
@jwt_required()
def create_review():
    uid = get_jwt_identity()
    data = request.get_json(silent=True) or {}
    booking_id = data.get("booking_id")
    comment = (data.get("comment") or "").strip()

    try:
        rating = int(data.get("rating"))
    except (TypeError, ValueError):
        return jsonify({"error": "Rating must be a number between 1 and 5."}), 400
    if rating < 1 or rating > 5:
        return jsonify({"error": "Rating must be between 1 and 5."}), 400

    booking = store.get_booking(booking_id)
    if not booking or str(booking["user_id"]) != str(uid):
        return jsonify({"error": "Booking not found."}), 404
    if booking["status"] != "completed":
        return jsonify({"error": "You can only rate a completed booking."}), 400
    if store.find_review_by_booking(booking["id"]):
        return jsonify({"error": "You have already rated this booking."}), 409

    review = store.create_review(
        {
            "booking_id": booking["id"],
            "user_id": booking["user_id"],
            "rating": rating,
            "comment": comment,
        }
    )
    return jsonify({"review": review_dict(review)}), 201
