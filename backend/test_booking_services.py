"""API tests for the multi-service booking behaviour (demo build, no database).

Covers:
1. Services expose the house-service flag.
2. A booking can hold SEVERAL services, and the price is their sum.
3. Bookings made only of non-house services skip the house details entirely.
4. A booking containing a house service still requires the house details.
5. The legacy single-service payload still works.
6. My Bookings and Admin Bookings return the full service lists.

Start the backend first, then:  .venv/bin/python test_booking_services.py
"""
import json
import random
import sys
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:5000/api"
passed = 0
failed = 0


def call(method, path, body=None, token=None):
    """Make an API call and return (status, parsed_json)."""
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(f"{BASE}{path}", data=data, method=method)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.status, json.loads(resp.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        try:
            return e.code, json.loads(raw or "{}")
        except ValueError:
            return e.code, {"raw": raw}


def check(label, condition, detail=""):
    global passed, failed
    if condition:
        passed += 1
        print(f"  PASS  {label}")
    else:
        failed += 1
        print(f"  FAIL  {label}  {detail}")


print("\n=== 0. Setup: create a fresh customer account ===")
stamp = random.randint(100000, 999999)
cust = {
    "first_name": "Test", "last_name": "Customer", "phone": f"0917{stamp:07d}",
    "email": f"cust{stamp}@example.com", "password": "secret123",
    "confirm_password": "secret123", "terms": True,
    "municipality": "City of San Fernando", "barangay": "Alasas",
}
status, res = call("POST", "/auth/signup", cust)
check("customer signup returns 201", status == 201, f"got {status} {res}")
token = res.get("token") or res.get("access_token")
check("customer has a token", bool(token))

print("\n=== 1. Services expose the house-service flag ===")
status, res = call("GET", "/site")
services = {s["id"]: s for s in res.get("services", [])}
check("GET /site returns services", status == 200 and len(services) > 0, f"got {status}")
home = next((s for s in services.values() if s["name"] == "Home Deep Cleaning"), None)
office = next((s for s in services.values() if s["name"] == "Office Cleaning"), None)
couch = next((s for s in services.values() if s["name"] == "Couch Cleaning"), None)
check("Home Deep Cleaning is a house service", home and home["is_house_service"] == 1)
check("Couch Cleaning is NOT a house service", couch and couch["is_house_service"] == 0)
check("there are non-house services seeded",
      sum(1 for s in services.values() if s["is_house_service"] == 0) >= 3)

print("\n=== 2. Booking with MULTIPLE house services ===")
status, res = call("POST", "/bookings", {
    "schedule_date": "2027-03-01", "service_ids": [home["id"], office["id"]],
    "municipality": "City of San Fernando", "barangay": "Alasas", "notes": "Two services please",
    "sqm": 80, "rooms": 3, "stories": 2,
}, token)
check("multi-service house booking created", status == 201, f"got {status} {res}")
booking = res.get("booking", {})
check("both services saved in service_ids", len(booking.get("service_ids", [])) == 2, str(booking.get("service_ids")))
check("both service names saved", len(booking.get("service_names", [])) == 2, str(booking.get("service_names")))
check("house details stored", booking.get("floor_area_sqm") == 80 and booking.get("rooms") == 3 and booking.get("stories") == 2)
# Home Deep: base 1500 + 20*80 + 300*3 + 500*2 = 5000, clamp 1500-5000 -> 5000
# Office:   base 2500 + 25*80 + 400*hours(0) = 4500, clamp 2500-8000 -> 4500
check("price is the SUM of both services (5000+4500=9500)", booking.get("price") == 9500, f"got {booking.get('price')}")

print("\n=== 2b. The new booking is visible straight away (in memory) ===")
status, res = call("GET", "/bookings", token=token)
mine = res.get("bookings", [])
check("the booking round-trips from the store",
      any(b["id"] == booking.get("id") for b in mine), f"got {len(mine)} bookings")

print("\n=== 3. Booking with ONLY a non-house service ===")
status, res = call("POST", "/bookings", {
    "schedule_date": "2027-03-02", "service_ids": [couch["id"]],
    "municipality": "City of San Fernando", "barangay": "Alasas", "notes": "Couch only",
    # Deliberately send NO house details - this must still succeed.
    "hours": 3,
}, token)
check("non-house booking succeeds with no house details", status == 201, f"got {status} {res}")
nb = res.get("booking", {})
check("house details saved as None", nb.get("floor_area_sqm") is None and nb.get("rooms") is None and nb.get("stories") is None,
      f"got sqm={nb.get('floor_area_sqm')} rooms={nb.get('rooms')} stories={nb.get('stories')}")
# Couch: base 1200 + 300*3 = 2100, clamp 1200-3500 -> 2100
check("non-house price uses hourly rate (2100)", nb.get("price") == 2100, f"got {nb.get('price')}")

print("\n=== 4. Booking with NO services is rejected ===")
status, res = call("POST", "/bookings", {
    "schedule_date": "2027-03-03", "service_ids": [],
    "municipality": "City of San Fernando", "barangay": "Alasas",
}, token)
check("empty service list -> 400", status == 400, f"got {status}")
check("error mentions at least one service", "at least one" in res.get("error", "").lower(), str(res))

print("\n=== 5. House service WITHOUT house details is rejected ===")
status, res = call("POST", "/bookings", {
    "schedule_date": "2027-03-04", "service_ids": [home["id"]],
    "municipality": "City of San Fernando", "barangay": "Alasas",
}, token)
check("house booking with no sqm -> 400", status == 400, f"got {status}")
check("error asks for the area", "square meters" in res.get("error", "").lower(), str(res))

print("\n=== 6. MIXED house + non-house still requires house details ===")
status, res = call("POST", "/bookings", {
    "schedule_date": "2027-03-05", "service_ids": [couch["id"], home["id"]],
    "municipality": "City of San Fernando", "barangay": "Alasas",
}, token)
check("mixed booking with no house details -> 400", status == 400, f"got {status}")

status, res = call("POST", "/bookings", {
    "schedule_date": "2027-03-05", "service_ids": [couch["id"], home["id"]],
    "municipality": "City of San Fernando", "barangay": "Alasas",
    "sqm": 60, "rooms": 2, "stories": 1, "hours": 2,
}, token)
check("mixed booking WITH house details -> 201", status == 201, f"got {status} {res}")
mixed = res.get("booking", {})
check("mixed booking keeps both services", len(mixed.get("service_names", [])) == 2, str(mixed.get("service_names")))
# Couch:  1200 base + 300/hr * 2 = 1800        -> clamp 1200-3500 -> 1800
# Home:   1500 + 20*60 + 300*2 + 500*1 + 250*2 = 4300 -> clamp 1500-5000 -> 4300
check("mixed price sums both (1800+4300=6100)", mixed.get("price") == 6100, f"got {mixed.get('price')}")

print("\n=== 7. Legacy single-service payload still works ===")
status, res = call("POST", "/bookings", {
    "schedule_date": "2027-03-06", "service_id": home["id"],
    "municipality": "City of San Fernando", "barangay": "Alasas",
    "sqm": 50, "rooms": 2, "stories": 1,
}, token)
check("old 'service_id' field still accepted", status == 201, f"got {status} {res}")
legacy = res.get("booking", {})
check("legacy booking normalised to a one-item list", legacy.get("service_ids") == [home["id"]], str(legacy.get("service_ids")))

print("\n=== 8. My Bookings returns the service lists ===")
status, res = call("GET", "/bookings", token=token)
check("GET /bookings -> 200", status == 200, f"got {status}")
mine = res.get("bookings", [])
check("bookings returned", len(mine) >= 4, f"got {len(mine)}")
multi = next((b for b in mine if len(b.get("service_ids", [])) == 2), None)
check("a multi-service booking round-trips", multi is not None)
check("multi-service names are a list of 2", multi and len(multi["service_names"]) == 2, str(multi and multi.get("service_names")))

print("\n=== 9. Admin bookings expose customer contact + services ===")
status, res = call("POST", "/auth/login", {"identifier": "admin@sparkleclean.ph", "password": "admin123"})
admin_token = res.get("token") or res.get("access_token")
check("admin login works (seeded sample admin)", bool(admin_token), f"got {status} {res}")
status, res = call("GET", "/admin/bookings", token=admin_token)
check("GET /admin/bookings -> 200", status == 200, f"got {status}")
ab = res.get("bookings", [])
check("admin sees bookings", len(ab) > 0, f"got {len(ab)}")
check("admin sees customer_email", all("customer_email" in b for b in ab))
check("admin sees customer_phone", all("customer_phone" in b for b in ab))
check("admin sees service_names list", any(len(b.get("service_names", [])) == 2 for b in ab))

print("\n=== 10. Admin can create a service with the house flag ===")
status, res = call("POST", "/admin/services", {
    "name": f"Test Non-House {stamp}", "description": "temp", "base_price": 500,
    "min_price": 500, "max_price": 900, "use_hour": 1, "price_per_hour": 200,
    "is_house_service": 0, "sort_order": 99,
}, token=admin_token)
check("admin created a service", status == 201, f"got {status} {res}")
new_svc = res.get("service", {})
check("new service keeps is_house_service=0", new_svc.get("is_house_service") == 0, str(new_svc.get("is_house_service")))

print("\n=== 11. Admin status update still drives payment/status ===")
status, res = call("PUT", f"/admin/bookings/{booking.get('id')}",
                   {"status": "confirmed", "payment_status": "partial", "downpayment": 1000},
                   token=admin_token)
check("admin updated the booking", status == 200, f"got {status} {res}")
upd = res.get("booking", {})
check("status saved", upd.get("status") == "confirmed", str(upd.get("status")))
check("downpayment saved", upd.get("downpayment") == 1000, str(upd.get("downpayment")))

print(f"\n{'=' * 60}")
print(f"RESULT: {passed} passed, {failed} failed")
print("=" * 60)
sys.exit(1 if failed else 0)
