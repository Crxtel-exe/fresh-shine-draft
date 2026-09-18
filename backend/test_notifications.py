"""Test the notification feature (demo build, no database).

Verifies:
1. send_email / send_sms log gracefully when nothing is configured.
2. Booking creation triggers notify_booking_created (email + SMS).
3. Admin status change triggers notify_booking_status.
4. Multi-service bookings list every service in the message.
5. A non-house booking has no area line.

This test imports the notification helpers directly, so it needs no server.
Run it with:  .venv/bin/python test_notifications.py
"""
import io
import logging
import os
import sys

# Ensure no SMTP/SMS config is present (test the graceful path).
for k in ("SMTP_HOST", "SMTP_PORT", "SMTP_USER", "SMTP_PASS", "MAIL_FROM",
          "SMS_PROVIDER", "SMS_API_KEY", "SMS_SENDER", "TWILIO_ACCOUNT_SID",
          "TWILIO_AUTH_TOKEN", "TWILIO_FROM"):
    os.environ.pop(k, None)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from notifications import notify_booking_created, notify_booking_status, send_email, send_sms

# Capture log output to assert messages are logged.
log_stream = io.StringIO()
handler = logging.StreamHandler(log_stream)
logging.getLogger("notifications").addHandler(handler)
logging.getLogger("notifications").setLevel(logging.INFO)

passed = 0
failed = 0


def check(label, condition, detail=""):
    global passed, failed
    if condition:
        passed += 1
        print(f"PASS: {label}")
    else:
        failed += 1
        print(f"FAIL: {label}  {detail}")


def reset_log():
    log_stream.truncate(0)
    log_stream.seek(0)


# --- Test 1: send_email / send_sms log when unconfigured ---
reset_log()
check("send_email returns False when unconfigured", send_email("a@b.com", "Subj", "Body") is False)
check("send_sms returns False when unconfigured", send_sms("09171234567", "Hello") is False)
log = log_stream.getvalue()
check("email is logged when unconfigured", "[EMAIL] (not configured)" in log, log)
check("sms is logged when unconfigured", "[SMS] (not configured)" in log, log)

# --- Test 2: notify_booking_created logs both (multi-service, with house details) ---
reset_log()
booking = {
    "service_name": "Home Deep Cleaning",
    "service_names": ["Home Deep Cleaning", "Couch Cleaning"],
    "schedule_date": "2026-09-10",
    "municipality": "San Fernando",
    "barang": "Dolores",
    "floor_area_sqm": 80,
    "rooms": 3,
    "stories": 2,
    "price": 7100.0,
}
user = {"first_name": "Juan", "email": "juan@test.com", "phone": "09171234567"}
notify_booking_created(booking, user)
log = log_stream.getvalue()
check("created: email logged", "[EMAIL] (not configured)" in log and "Booking Confirmation" in log, log)
check("created: SMS logged", "[SMS] (not configured)" in log and "Booking confirmed" in log, log)
check("created: BOTH services listed", "Home Deep Cleaning, Couch Cleaning" in log, log)
check("created: area line present for a house booking", "Area: 80 sqm" in log, log)
check("created: price formatted", "7,100.00" in log, log)

# --- Test 2b: a non-house booking has no area line ---
reset_log()
couch_only = {
    "service_name": "Couch Cleaning",
    "service_names": ["Couch Cleaning"],
    "schedule_date": "2026-09-11",
    "municipality": "San Fernando",
    "barang": "Dolores",
    "floor_area_sqm": None,
    "rooms": None,
    "stories": None,
    "price": 2100.0,
}
notify_booking_created(couch_only, user)
log = log_stream.getvalue()
check("non-house: no area line", "Area:" not in log, log)
check("non-house: service still listed", "Couch Cleaning" in log, log)

# --- Test 3: notify_booking_status logs on status change, skips if unchanged ---
reset_log()
notify_booking_status(
    booking,
    {"name": "Juan Dela Cruz", "email": "juan@test.com", "phone": "09171234567"},
    "pending",
    "confirmed",
)
log = log_stream.getvalue()
check("status: email logged", "[EMAIL] (not configured)" in log and "Booking Confirmed" in log, log)
check("status: SMS logged", "[SMS] (not configured)" in log and "now confirmed" in log, log)

reset_log()
notify_booking_status(
    booking,
    {"name": "Juan Dela Cruz", "email": "juan@test.com", "phone": "09171234567"},
    "confirmed",
    "confirmed",
)
check("status: nothing sent when the status did not change", log_stream.getvalue().strip() == "", log_stream.getvalue())

print(f"\n{'=' * 60}")
print(f"RESULT: {passed} passed, {failed} failed")
print("=" * 60)
sys.exit(1 if failed else 0)
