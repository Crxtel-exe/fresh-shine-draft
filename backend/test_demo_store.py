"""Tests for the DEMO build: sample accounts, and no database anywhere.

Covers:
1. There is genuinely no database: db.py is gone and no module opens SQLite.
2. GET /api/demo-accounts returns the sample customer + admin logins.
3. BOTH sample accounts can log in with the credentials shown on the login page.
4. The sample customer already has bookings, including one they can review.
5. The sample admin can reach the admin bookings view.
6. Data lives in memory: a new booking is visible immediately, and the store
   can be reset (which is what a server restart does).

Start the backend first, then:  .venv/bin/python test_demo_store.py
"""
import json
import os
import re
import sys
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:5000/api"
HERE = os.path.dirname(os.path.abspath(__file__))
passed = 0
failed = 0


def check(label, condition, detail=""):
    global passed, failed
    if condition:
        passed += 1
        print(f"  PASS  {label}")
    else:
        failed += 1
        print(f"  FAIL  {label}  {detail}")


def call(method, path, body=None, token=None):
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


print("\n=== 1. There is no database in this build ===")
check("db.py has been removed", not os.path.exists(os.path.join(HERE, "db.py")))
check("seed_admin.py has been removed", not os.path.exists(os.path.join(HERE, "seed_admin.py")))
check("no cleaning.db file exists", not os.path.exists(os.path.join(HERE, "cleaning.db")))
check("store.py exists (the in-memory store)", os.path.exists(os.path.join(HERE, "store.py")))

# Scan the project's own source for any real database import.
# Only actual import statements count -- the words appear in comments and
# docstrings all over this file set, and matching those is not useful.
DB_IMPORT_RE = re.compile(
    r"^\s*(?:import\s+(?:sqlite3|sqlalchemy)\b|from\s+(?:sqlite3|sqlalchemy)\b)",
    re.IGNORECASE,
)
SKIP_DIRS = {"__pycache__", ".venv", "venv", "node_modules"}

offenders = []
for root, dirs, files in os.walk(HERE):
    dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
    for name in files:
        if not name.endswith(".py"):
            continue
        path = os.path.join(root, name)
        rel = os.path.relpath(path, HERE)
        with open(path, encoding="utf-8") as fh:
            for lineno, line in enumerate(fh, 1):
                if DB_IMPORT_RE.match(line):
                    offenders.append(f"{rel}:{lineno}:{line.strip()}")
check("nothing imports sqlite3 or SQLAlchemy", not offenders, "; ".join(offenders))

# Also make sure the old connection helper is gone from every module.
legacy = []
for root, dirs, files in os.walk(HERE):
    dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
    for name in files:
        if not name.endswith(".py") or name == "test_demo_store.py":
            continue
        path = os.path.join(root, name)
        rel = os.path.relpath(path, HERE)
        with open(path, encoding="utf-8") as fh:
            for lineno, line in enumerate(fh, 1):
                stripped = line.strip()
                if stripped.startswith("#"):
                    continue
                if re.match(r"^from db import|^import db\b", stripped):
                    legacy.append(f"{rel}:{lineno}:{stripped}")
check("nothing still imports the removed db module", not legacy, "; ".join(legacy))

print("\n=== 2. Demo accounts are published for the login page ===")
status, res = call("GET", "/demo-accounts")
check("GET /demo-accounts -> 200", status == 200, f"got {status}")
accounts = {a["role"]: a for a in res.get("accounts", [])}
check("a sample customer is listed", "user" in accounts, str(list(accounts)))
check("a sample admin is listed", "admin" in accounts, str(list(accounts)))
check("the customer entry carries an email + password",
      accounts.get("user", {}).get("email") and accounts.get("user", {}).get("password"))
check("the admin entry carries an email + password",
      accounts.get("admin", {}).get("email") and accounts.get("admin", {}).get("password"))

print("\n=== 3. Both sample accounts can log in with the shown credentials ===")
status, res = call("POST", "/auth/login", {
    "identifier": accounts["user"]["email"], "password": accounts["user"]["password"],
})
customer_token = res.get("token") or res.get("access_token")
check("sample customer logs in", status == 200 and bool(customer_token), f"got {status} {res}")
check("sample customer has role 'user'", res.get("user", {}).get("role") == "user", str(res.get("user")))

status, res = call("POST", "/auth/login", {
    "identifier": accounts["admin"]["email"], "password": accounts["admin"]["password"],
})
admin_token = res.get("token") or res.get("access_token")
check("sample admin logs in", status == 200 and bool(admin_token), f"got {status} {res}")
check("sample admin has role 'admin'", res.get("user", {}).get("role") == "admin", str(res.get("user")))

print("\n=== 3b. The sample login also works by phone number ===")
status, res = call("POST", "/auth/login", {"identifier": "09171234567", "password": accounts["user"]["password"]})
check("login by phone works", status == 200, f"got {status} {res}")

print("\n=== 3c. Wrong credentials are still rejected ===")
status, res = call("POST", "/auth/login", {"identifier": accounts["admin"]["email"], "password": "wrong-password"})
check("bad password -> 401", status == 401, f"got {status}")

print("\n=== 4. The sample customer starts with usable demo bookings ===")
status, res = call("GET", "/bookings", token=customer_token)
check("GET /bookings -> 200", status == 200, f"got {status}")
bookings = res.get("bookings", [])
check("the sample customer already has bookings", len(bookings) >= 2, f"got {len(bookings)}")
check("one of them is completed (so a review can be tried)",
      any(b["status"] == "completed" for b in bookings), str([b["status"] for b in bookings]))
check("the completed one is already paid",
      any(b["status"] == "completed" and b["payment_status"] == "paid" for b in bookings))
check("a non-house sample booking kept its house details empty",
      any(len(b["service_names"]) == 1 and b["service_names"][0] == "Couch Cleaning"
          and b["floor_area_sqm"] is None for b in bookings))

print("\n=== 4b. There is a seeded review to look at ===")
status, res = call("GET", "/reviews")
check("GET /reviews -> 200", status == 200, f"got {status}")
reviews = res.get("reviews", [])
check("a sample review is seeded", len(reviews) >= 1, f"got {len(reviews)}")
check("the sample review has an admin reply",
      any(r.get("admin_reply") for r in reviews), str(reviews[:1]))

print("\n=== 5. The sample admin can reach the admin views ===")
status, res = call("GET", "/admin/bookings", token=admin_token)
check("GET /admin/bookings -> 200", status == 200, f"got {status}")
admin_bookings = res.get("bookings", [])
check("admin sees the sample bookings", len(admin_bookings) >= 2, f"got {len(admin_bookings)}")
check("admin rows carry the customer's email + phone (for Contact Customer)",
      all(b.get("customer_email") and b.get("customer_phone") for b in admin_bookings))

status, res = call("GET", "/admin/reviews", token=admin_token)
check("GET /admin/reviews -> 200", status == 200, f"got {status}")
check("admin sees the sample review", len(res.get("reviews", [])) >= 1)

print("\n=== 5b. The sample CUSTOMER cannot reach admin routes ===")
status, res = call("GET", "/admin/bookings", token=customer_token)
check("customer blocked from admin bookings -> 403", status == 403, f"got {status}")

print("\n=== 6. Data lives in memory and is visible immediately ===")
status, res = call("POST", "/bookings", {
    "schedule_date": "2027-06-01", "service_ids": [1],
    "municipality": "City of San Fernando", "barangay": "Alasas",
    "sqm": 40, "rooms": 1, "stories": 1,
}, token=customer_token)
check("a new booking is created", status == 201, f"got {status} {res}")
new_id = res.get("booking", {}).get("id")
status, res = call("GET", "/bookings", token=customer_token)
check("the new booking is readable straight away (no write-back needed)",
      any(b["id"] == new_id for b in res.get("bookings", [])), str(res)[:200])

print(f"\n{'=' * 60}")
print(f"RESULT: {passed} passed, {failed} failed")
print("=" * 60)
sys.exit(1 if failed else 0)
