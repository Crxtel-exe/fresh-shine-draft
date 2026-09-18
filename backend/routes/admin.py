"""Admin routes: bookings, reviews and logout.

Website content is intentionally code-managed in backend/store.py, so the admin
panel does not expose service, project, homepage-image, logo, or company-info
editing endpoints.
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, jwt_required

import store
from helpers import admin_required, booking_dict, review_dict
from notifications import notify_booking_status

bp = Blueprint("admin", __name__, url_prefix="/api/admin")

SITE_FIELDS = [
    "company_name", "tagline", "description", "about", "location",
    "email", "phone", "facebook", "tiktok",
]


# ---------------------------------------------------------------------------
# Logout
# ---------------------------------------------------------------------------
@bp.post("/logout")
@jwt_required()
def admin_logout():
    """Invalidate the current admin token so it can no longer be used."""
    store.block_token(get_jwt()["jti"])
    return jsonify({"message": "Logged out successfully."})


# ---------------------------------------------------------------------------
# Bookings
# ---------------------------------------------------------------------------
@bp.get("/bookings")
@admin_required
def admin_bookings():
    rows = store.list_all_bookings()
    return jsonify(
        {
            "bookings": [
                {
                    **booking_dict(r),
                    "customer_name": r["customer_name"],
                    "customer_phone": r["customer_phone"],
                    "customer_email": r["customer_email"],
                }
                for r in rows
            ]
        }
    )


@bp.put("/bookings/<int:bid>")
@admin_required
def admin_update_booking(bid):
    data = request.get_json(silent=True) or {}
    booking = store.get_booking(bid)
    if not booking:
        return jsonify({"error": "Booking not found."}), 404

    old_status = booking["status"]
    new_status = data.get("status", booking["status"])

    updated = store.update_booking(
        bid,
        {
            "status": new_status,
            "payment_status": data.get("payment_status", booking["payment_status"]),
            "downpayment": data.get("downpayment", booking["downpayment"]),
        },
    )

    # Notify the customer when the booking status changes.
    user = store.get_user(booking["user_id"])
    if user:
        notify_booking_status(
            updated,
            {
                "name": f"{user['first_name']} {user['last_name']}",
                "email": user["email"],
                "phone": user["phone"],
            },
            old_status,
            new_status,
        )

    return jsonify({"booking": booking_dict(updated)})


# ---------------------------------------------------------------------------
# Reviews
# ---------------------------------------------------------------------------
@bp.get("/reviews")
@admin_required
def admin_reviews():
    rows = store.list_reviews(with_user=True)
    return jsonify(
        {
            "reviews": [
                {
                    **review_dict(r),
                    "customer_name": r["customer_name"],
                    "service_name": r["service_name"],
                    "schedule_date": r["schedule_date"],
                }
                for r in rows
            ]
        }
    )


@bp.put("/reviews/<int:rid>")
@admin_required
def admin_reply_review(rid):
    reply = (request.get_json(silent=True) or {}).get("admin_reply") or ""
    review = store.get_review(rid)
    if not review:
        return jsonify({"error": "Review not found."}), 404
    updated = store.update_review(rid, {"admin_reply": reply})
    return jsonify({"review": review_dict(updated)})


# ---------------------------------------------------------------------------
# Site content, services, and homepage projects are code-managed.
# There are intentionally no admin endpoints for editing these values.
# Edit backend/store.py and the frontend public assets instead.
# ---------------------------------------------------------------------------
