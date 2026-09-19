"""Shared helpers: serializers, validation, and auth decorators.

DEMO BUILD -- nothing here touches a database. Every lookup goes through the
in-memory store (see `store.py`), which is seeded on startup and reset when the
server restarts.
"""
import json
import re
from functools import wraps

from flask import jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

import store
from pampanga import PAMPANGA

# Re-exported so the routes keep importing them from here.
from store import check_password, hash_password  # noqa: F401

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_RE = re.compile(r"^(\+?63|0)?9\d{9}$")


# ---------------------------------------------------------------------------
# Serializers
# ---------------------------------------------------------------------------
def public_user(u):
    return {
        "id": u["id"],
        "first_name": u["first_name"],
        "last_name": u["last_name"],
        "phone": u["phone"],
        "email": u["email"],
        "role": u["role"],
        "municipality": u["municipality"],
        "barangay": u["barangay"],
        "address": u["address"],
        "profile_pic": u["profile_pic"],
    }


def _as_ids(raw):
    """Normalise a stored service-id list into a list of ints.

    The store holds real lists; a JSON string is still accepted so any older
    saved shape keeps working.
    """
    if not raw:
        return []
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except (TypeError, ValueError):
            return []
    if not isinstance(raw, list):
        return []
    out = []
    for v in raw:
        try:
            out.append(int(v))
        except (TypeError, ValueError):
            continue
    return out


def _as_names(raw):
    """Normalise a stored service-name list into a list of strings."""
    if not raw:
        return []
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except (TypeError, ValueError):
            return []
    if not isinstance(raw, list):
        return []
    return [str(v) for v in raw]


def booking_dict(b):
    """Serialize a booking.

    A booking can cover more than one service. `service_ids` and `service_names`
    hold the full list; `service_id` / `service_name` keep the first service so
    older screens still work.
    """
    return {
        "id": b["id"],
        "user_id": b["user_id"],
        "service_id": b["service_id"],
        "service_name": b["service_name"],
        "service_ids": _as_ids(b.get("service_ids")),
        "service_names": _as_names(b.get("service_names"))
        or ([b["service_name"]] if b.get("service_name") else []),
        "floor_area_sqm": b.get("floor_area_sqm"),
        "rooms": b.get("rooms"),
        "stories": b.get("stories"),
        "schedule_date": b["schedule_date"],
        "municipality": b["municipality"],
        "barang": b["barang"],
        "notes": b.get("notes"),
        "status": b["status"],
        "payment_status": b["payment_status"],
        "downpayment": b.get("downpayment"),
        "price": b.get("price"),
        "created_at": b.get("created_at"),
    }


def review_dict(r):
    return {
        "id": r["id"],
        "booking_id": r["booking_id"],
        "user_id": r["user_id"],
        "rating": r["rating"],
        "comment": r.get("comment"),
        "admin_reply": r.get("admin_reply"),
        "created_at": r.get("created_at"),
    }


def service_dict(s):
    """Serialize a service including its price range and pricing options."""
    return {
        "id": s["id"],
        "name": s["name"],
        "description": s.get("description"),
        "image": s.get("image"),
        "min_price": s.get("min_price"),
        "max_price": s.get("max_price"),
        "base_price": s.get("base_price"),
        "price_per_sqm": s.get("price_per_sqm"),
        "price_per_room": s.get("price_per_room"),
        "price_per_story": s.get("price_per_story"),
        "price_per_hour": s.get("price_per_hour"),
        "use_sqm": s.get("use_sqm"),
        "use_room": s.get("use_room"),
        "use_story": s.get("use_story"),
        "use_hour": s.get("use_hour"),
        "is_house_service": s.get("is_house_service"),
        "sort_order": s.get("sort_order"),
    }


def compute_price(service, options):
    """Estimate a service price from its pricing options.

    `options` is a dict with optional keys: sqm, rooms, stories, hours. The
    estimate is the base price plus each enabled option's rate times its
    quantity, clamped to the service's min/max range.
    """
    total = float(service["base_price"] or 0)
    if service["use_sqm"]:
        total += float(service["price_per_sqm"] or 0) * float(options.get("sqm") or 0)
    if service["use_room"]:
        total += float(service["price_per_room"] or 0) * float(options.get("rooms") or 0)
    if service["use_story"]:
        total += float(service["price_per_story"] or 0) * float(options.get("stories") or 0)
    if service["use_hour"]:
        total += float(service["price_per_hour"] or 0) * float(options.get("hours") or 0)

    lo = service["min_price"]
    hi = service["max_price"]
    if lo is not None and total < lo:
        total = lo
    if hi is not None and total > hi:
        total = hi
    return round(total, 2)


def compute_bookings_total(services, options):
    """Estimate the total for a booking covering one or more services.

    Each service is priced on its own with `compute_price`, then the results are
    added together. That means each service is clamped to its own min/max range
    before the sum, which is the intended behaviour: a cheap add-on stays at its
    own floor instead of being swallowed by another service's range.
    """
    return round(sum(compute_price(s, options) for s in services), 2)


def is_house_service(service):
    """Return True if this service needs house details (sqm, rooms, stories)."""
    return bool(service["is_house_service"])


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------
def valid_pampanga(municipality, barangay):
    """Return True if the municipality/barangay pair is a valid Pampanga location."""
    return municipality in PAMPANGA and barangay in PAMPANGA[municipality]


# ---------------------------------------------------------------------------
# Auth decorators
# ---------------------------------------------------------------------------
def get_current_user():
    """The logged-in user as a dict, or None if the account has gone away."""
    identity = get_jwt_identity()
    try:
        uid = int(identity)
    except (TypeError, ValueError):
        return None
    return store.get_user(uid)


def is_admin(user_id):
    try:
        uid = int(user_id)
    except (TypeError, ValueError):
        return False
    user = store.get_user(uid)
    return user is not None and user["role"] == "admin"


def admin_required(fn):
    @jwt_required()
    def wrapper(*args, **kwargs):
        if not is_admin(get_jwt_identity()):
            return jsonify({"error": "Admin access required"}), 403
        return fn(*args, **kwargs)

    wrapper.__name__ = fn.__name__
    return wrapper
