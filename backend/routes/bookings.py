"""Booking routes: user bookings, availability, downpayment, full payment.

DEMO BUILD: bookings live in memory and are cleared when the server restarts.
"""
from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

import store
from helpers import (
    booking_dict,
    compute_bookings_total,
    is_house_service,
    valid_pampanga,
)
from notifications import notify_booking_created

bp = Blueprint("bookings", __name__, url_prefix="/api/bookings")


@bp.get("")
@jwt_required()
def my_bookings():
    uid = get_jwt_identity()
    rows = store.list_bookings_for_user(uid)
    return jsonify({"bookings": [booking_dict(r) for r in rows]})


@bp.get("/availability")
@jwt_required()
def availability():
    return jsonify({"dates": store.availability_by_date()})


@bp.post("")
@jwt_required()
def create_booking():
    uid = get_jwt_identity()
    data = request.get_json(silent=True) or {}

    schedule_date = (data.get("schedule_date") or "").strip()
    municipality = (data.get("municipality") or "").strip()
    barangay = (data.get("barangay") or "").strip()
    notes = (data.get("notes") or "").strip()

    # The customer may tick several services in one booking. `service_ids` is the
    # current field; `service_id` is still accepted so older clients work.
    raw_ids = data.get("service_ids")
    if raw_ids is None:
        raw_ids = [data.get("service_id")] if data.get("service_id") else []
    if not isinstance(raw_ids, list):
        raw_ids = [raw_ids]

    service_ids = []
    for raw in raw_ids:
        try:
            sid = int(raw)
        except (TypeError, ValueError):
            continue
        if sid not in service_ids:
            service_ids.append(sid)

    if not service_ids:
        return jsonify({"error": "Please choose at least one cleaning service."}), 400

    if not schedule_date:
        return jsonify({"error": "Please select a date."}), 400
    if not valid_pampanga(municipality, barangay):
        return jsonify({"error": "Please choose a valid Pampanga location."}), 400

    # Validate the date is not in the past
    try:
        chosen = datetime.strptime(schedule_date, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "Invalid date format."}), 400
    if chosen < datetime.now().date():
        return jsonify({"error": "You cannot book a date in the past."}), 400

    services = []
    for sid in service_ids:
        service = store.get_service(sid)
        if not service:
            return jsonify({"error": "One of the selected services was not found."}), 400
        services.append(service)

    # House details (floor area, rooms, stories) only apply when the customer
    # picked at least one house cleaning service. For non-house services such as
    # couch cleaning they are neither required nor stored.
    needs_house_details = any(is_house_service(s) for s in services)

    sqm = rooms = stories = None
    if needs_house_details:
        try:
            sqm = float(data.get("sqm") or 0)
            rooms = int(data.get("rooms") or 0)
            stories = int(data.get("stories") or 0)
        except (TypeError, ValueError):
            return jsonify({"error": "Please enter valid area details."}), 400
        if sqm <= 0:
            return jsonify({"error": "Please enter the area in square meters (sqm)."}), 400
        if rooms <= 0:
            return jsonify({"error": "Please enter the number of rooms."}), 400
        if stories <= 0:
            return jsonify({"error": "Please enter the number of stories/floors."}), 400

    try:
        hours = float(data.get("hours") or 0)
    except (TypeError, ValueError):
        hours = 0

    # Compute the estimated price: each selected service priced on its own, then
    # added together.
    price = compute_bookings_total(
        services,
        {"sqm": sqm or 0, "rooms": rooms or 0, "stories": stories or 0, "hours": hours},
    )

    # Conflict logic: only 1 booking per day unless a downpayment secures it.
    existing = store.list_bookings_on_date(schedule_date)
    if existing and not any((b.get("downpayment") or 0) > 0 for b in existing):
        return jsonify(
            {
                "error": "This date is already booked. You can secure it by paying a downpayment (first downpayment, first served)."
            }
        ), 409

    # service_id / service_name keep the first service for older screens;
    # service_ids / service_names hold the full list.
    names = [s["name"] for s in services]
    booking = store.create_booking(
        {
            "user_id": int(uid),
            "service_id": service_ids[0],
            "service_name": names[0],
            "service_ids": service_ids,
            "service_names": names,
            "floor_area_sqm": sqm,
            "rooms": rooms,
            "stories": stories,
            "schedule_date": schedule_date,
            "municipality": municipality,
            "barang": barangay,
            "notes": notes,
            "status": "pending",
            "payment_status": "unpaid",
            "price": price,
        }
    )

    # Send confirmation email + SMS (gracefully skipped if not configured).
    notify_booking_created(booking, store.get_user(uid) or {})

    return jsonify({"booking": booking_dict(booking)}), 201


@bp.post("/<int:bid>/downpayment")
@jwt_required()
def pay_downpayment(bid):
    uid = get_jwt_identity()
    amount = float((request.get_json(silent=True) or {}).get("amount") or 0)
    if amount <= 0:
        return jsonify({"error": "Please enter a valid downpayment amount."}), 400

    booking = store.get_booking(bid)
    if not booking or str(booking["user_id"]) != str(uid):
        return jsonify({"error": "Booking not found."}), 404

    # First downpayment first serve: if another booking already secured this date, reject.
    if store.find_secured_booking(booking["schedule_date"], exclude_id=bid):
        return jsonify({"error": "This date has already been secured by another customer."}), 409

    updated = store.update_booking(bid, {"downpayment": amount, "payment_status": "partial"})
    return jsonify({"booking": booking_dict(updated)})


@bp.post("/<int:bid>/payfull")
@jwt_required()
def pay_full(bid):
    uid = get_jwt_identity()
    booking = store.get_booking(bid)
    if not booking or str(booking["user_id"]) != str(uid):
        return jsonify({"error": "Booking not found."}), 404
    updated = store.update_booking(bid, {"payment_status": "paid"})
    return jsonify({"booking": booking_dict(updated)})
