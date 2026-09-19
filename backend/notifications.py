"""Email and SMS notification helpers.

Both functions are designed to fail gracefully: if the relevant configuration
is missing (e.g. during local development), they log the message instead of
raising, so the app keeps working without any notification provider set up.

Configuration is read from environment variables (see README for details):

Email (SMTP):
    SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, MAIL_FROM

SMS (provider):
    SMS_PROVIDER  (e.g. "twilio" or "generic")
    SMS_API_KEY, SMS_SENDER
    Twilio also needs: TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM
"""
import json
import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from urllib.parse import urlencode
from urllib.request import Request, urlopen

logger = logging.getLogger("notifications")


# ---------------------------------------------------------------------------
# Email (SMTP)
# ---------------------------------------------------------------------------
def _smtp_config():
    """Return a dict of SMTP settings, or None if SMTP is not configured."""
    host = os.environ.get("SMTP_HOST")
    if not host:
        return None
    return {
        "host": host,
        "port": int(os.environ.get("SMTP_PORT", "587")),
        "user": os.environ.get("SMTP_USER", ""),
        "password": os.environ.get("SMTP_PASS", ""),
        "mail_from": os.environ.get("MAIL_FROM", os.environ.get("SMTP_USER", "no-reply@sparkleclean.ph")),
    }


def send_email(to, subject, body, html=None):
    """Send an email via SMTP. Logs the message if SMTP is not configured.

    Returns True on success, False if it was only logged (or failed).
    """
    cfg = _smtp_config()
    if cfg is None:
        logger.info("[EMAIL] (not configured) To=%s Subject=%s\n%s", to, subject, body)
        return False

    msg = MIMEMultipart("alternative")
    msg["From"] = cfg["mail_from"]
    msg["To"] = to
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))
    if html:
        msg.attach(MIMEText(html, "html", "utf-8"))

    try:
        with smtplib.SMTP(cfg["host"], cfg["port"], timeout=15) as server:
            server.ehlo()
            if cfg["port"] == 587:
                server.starttls()
            if cfg["user"]:
                server.login(cfg["user"], cfg["password"])
            server.sendmail(cfg["mail_from"], [to], msg.as_string())
        logger.info("Email sent to %s", to)
        return True
    except Exception as exc:  # noqa: BLE001 - never break the app on email failure
        logger.warning("Failed to send email to %s: %s", to, exc)
        return False


# ---------------------------------------------------------------------------
# SMS
# ---------------------------------------------------------------------------
def _sms_config():
    """Return SMS provider settings, or None if SMS is not configured."""
    provider = os.environ.get("SMS_PROVIDER")
    if not provider:
        return None
    return {
        "provider": provider.lower(),
        "api_key": os.environ.get("SMS_API_KEY", ""),
        "sender": os.environ.get("SMS_SENDER", "SparkleClean"),
        "twilio_sid": os.environ.get("TWILIO_ACCOUNT_SID", ""),
        "twilio_token": os.environ.get("TWILIO_AUTH_TOKEN", ""),
        "twilio_from": os.environ.get("TWILIO_FROM", ""),
    }


def _send_twilio(cfg, to, message):
    """Send an SMS through the Twilio REST API."""
    from base64 import b64encode

    url = f"https://api.twilio.com/2010-04-01/Accounts/{cfg['twilio_sid']}/Messages.json"
    data = urlencode({"To": to, "From": cfg["twilio_from"], "Body": message}).encode()
    auth = b64encode(f"{cfg['twilio_sid']}:{cfg['twilio_token']}".encode()).decode()
    req = Request(url, data=data, headers={"Authorization": f"Basic {auth}"})
    with urlopen(req, timeout=15) as resp:
        return resp.status == 201


def _send_generic(cfg, to, message):
    """Send an SMS via a simple HTTP gateway.

    The gateway is expected to accept a GET/POST with query params:
    `to`, `message`, `sender`, and `api_key`. Override the endpoint with
    SMS_GATEWAY_URL if your provider differs.
    """
    endpoint = os.environ.get("SMS_GATEWAY_URL", "https://sms.example.com/send")
    params = urlencode(
        {"to": to, "message": message, "sender": cfg["sender"], "api_key": cfg["api_key"]}
    )
    req = Request(f"{endpoint}?{params}")
    with urlopen(req, timeout=15) as resp:
        return resp.status < 300


def send_sms(to: str, message: str):
    """Send an SMS via the configured provider. Logs if not configured."""
    cfg = _sms_config()
    if cfg is None:
        logger.info("[SMS] (not configured) to=%s\n%s", to, message)
        return False

    try:
        if cfg["provider"] == "twilio":
            _send_twilio(cfg, to, message)
        else:
            _send_generic(cfg, to, message)
        logger.info("SMS sent to %s", to)
        return True
    except Exception as exc:  # noqa: BLE001 - never break the app on SMS failure
        logger.warning("Failed to send SMS to %s: %s", to, exc)
        return False


# ---------------------------------------------------------------------------
# Booking notification helpers
# ---------------------------------------------------------------------------
def _service_list(code):
    """Turn a stored list of service names into text for notifications.

    The demo store keeps a real list; a JSON string is still accepted so any
    other shape keeps working.
    """
    if not code:
        return ""
    parsed = code
    if isinstance(code, str):
        try:
            parsed = json.loads(code)
        except (TypeError, ValueError):
            return code
    if not isinstance(parsed, list):
        return str(parsed)
    return ", ".join(str(v) for v in parsed)


def notify_booking_created(booking, user):
    """Send confirmation email + SMS when a booking is created."""
    subject = "Booking Confirmation - Fresh & Shine Cleaning Services"
    # A booking can cover several services; fall back to the single service name.
    services = _service_list(booking["service_names"]) or booking["service_name"] or ""
    # House details are only collected for house cleaning services.
    area_line = ""
    if booking["floor_area_sqm"]:
        area_line = (
            f"Area: {booking['floor_area_sqm']:g} sqm, "
            f"{booking['rooms']} room(s), {booking['stories']} story/ies\n"
        )
    body = (
        f"Hi {user['first_name']},\n\n"
        f"Your booking has been received!\n\n"
        f"Service(s): {services}\n"
        f"Date: {booking['schedule_date']}\n"
        f"Location: {booking['municipality']}, {booking['barang']}\n"
        f"{area_line}"
        f"Estimated price: \u20b1{booking['price']:,.2f}\n\n"
        f"An admin will call you to confirm your booking by paying a downpayment.\n\n"
        f"Thank you for choosing Fresh & Shine Cleaning Services!"
    )
    send_email(user["email"], subject, body)
    send_sms(
        user["phone"],
        f"Fresh & Shine Cleaning Services: Booking confirmed for {services} on "
        f"{booking['schedule_date']}. An admin will call to confirm your downpayment.",
    )


def notify_booking_status(booking, user, old_status, new_status):
    """Send an email when an admin changes a booking's status."""
    if old_status == new_status:
        return
    subject = f"Booking {new_status.title()} - Fresh & Shine Cleaning Services"
    body = (
        f"Dear {user['name']},\n\n"
        f"Your booking status has been updated.\n\n"
        f"Service: {booking['service_name']}\n"
        f"Date: {booking['schedule_date']}\n"
        f"Status: {old_status} \u2192 {new_status}\n\n"
        f"Thank you for choosing Fresh & Shine Cleaning Services!"
    )
    send_email(user["email"], subject, body)
    send_sms(
        user["phone"],
        f"Fresh & Shine Cleaning Services: Your booking ({booking['service_name']}) is now {new_status}.",
    )