"""Fresh & Shine Cleaning Services -- in-memory demo data store.

This is the DEMO build. There is NO database anywhere in this project: no
SQLite file, no SQLAlchemy, no migrations and no seed script to run.

Everything the app needs -- users, services, bookings, reviews, site content
and projects -- lives in the plain Python dictionaries below, inside the
running server process. Data is seeded on startup and is lost when the server
restarts. That is exactly what a demo wants: start it and it just works.

Every read returns a *copy*, and every write goes through one of the functions
at the bottom of this file, so the routes never mutate shared state by accident.
"""
from __future__ import annotations

import copy
import threading
from datetime import datetime

# ---------------------------------------------------------------------------
# Sample demo accounts
#
# These are created on startup so the app is usable immediately. They are shown
# on the login page (the backend serves them from /api/demo-accounts) so anyone
# can sign in without signing up first.
# ---------------------------------------------------------------------------
SAMPLE_ADMIN_EMAIL = "admin@sparkleclean.ph"
SAMPLE_ADMIN_PASSWORD = "admin123"
SAMPLE_CUSTOMER_EMAIL = "customer@sparkleclean.ph"
SAMPLE_CUSTOMER_PASSWORD = "customer123"

PASSWORD_MIN_LENGTH = 6

# ---------------------------------------------------------------------------
# Code-managed site content. Edit these dictionaries directly to change the public website.
# ---------------------------------------------------------------------------
DEFAULT_SITE = {
    "id": 1,
    "company_name": "Fresh & Shine Cleaning Services",
    "tagline": "Clean Spaces. Brighter Places.",
    "description": "Your home, our passion. Professional cleaning services across Pampanga.",
    "about": "Fresh & Shine Cleaning Services is a professional cleaning company. "
    "We provide reliable, high-quality cleaning services for homes and offices. "
    "Our team is trained, insured, and committed to making your space sparkle.",
    "location": "Lot 21 Block 15, Richtofen Cor. Pear St. Hensonville Homes, Barangay Malabanias, Angeles City, Pampanga",
    "email": "hello@freshshine.ph",
    "phone": "0960 662 7021",
    "facebook": "https://www.facebook.com/people/Fresh-Shine-Cleaning-Services/61590070245356/",
    "tiktok": "https://tiktok.com/@sparklecleanph",
    "updated_at": None,
}

# Pricing fields are kept explicit so services can be edited directly in this file.
DEFAULT_SERVICES = [
    # --- House cleaning services (is_house_service = 1) ---
    # These are the services that ask for the house details on the Booking page:
    # floor area (sqm), number of rooms and number of stories.
    {
        "name": "Condo Cleaning",
        "description": "blank muna",
        "image": "https://scontent.fcrk2-2.fna.fbcdn.net/v/t39.30808-6/814740951_122124524781335674_944118156304744472_n.jpg?stp=cp6_dst-jpg_tt6&cstp=mx1536x2048&ctp=s590x590&_nc_cat=110&_nc_map=urlgen_bucketless&ccb=1-7&_nc_sid=833d8c&_nc_eui2=AeG5qoN4H5yJdsdaZiXFqBBUbg3--MQynsFuDf74xDKewd1PoQzUtPcTqyow-ooSGOa3YvP92Jk-cOKTLHSijmfw&_nc_ohc=INH5YNN8es8Q7kNvwG6TGDM&_nc_oc=AdpK46n0eIQ6cjr2Jn1U5i4MO8nr4KbpsJiEvp-vl6lYVHxo6vnOHYmrwJx_7tWkj2c&_nc_zt=23&_nc_ht=scontent.fcrk2-2.fna&_nc_gid=nPTEeejJUHCMiJXTIkgFRQ&_nc_ss=7b2a8&oh=00_AQIFcPfeJ06VSEYbDTkiOoYHHCALrDcmn-wpLAvU_U-JeA&oe=6AB328AC",
        "min_price": 0, "max_price": 0, "base_price": 1500,
        "price_per_sqm": 20, "price_per_room": 300, "price_per_story": 500, "price_per_hour": 250,
        "use_sqm": 1, "use_room": 1, "use_story": 1, "use_hour": 1,
        "is_house_service": 1, "sort_order": 1,
    },
    {
        "name": "House Deep Cleaning",
        "description": "blank for now",
        "image": "https://scontent.fcrk4-1.fna.fbcdn.net/v/t39.30808-6/750585691_122113357473335674_2047172829682699588_n.jpg?stp=dst-jpg_tt6&cstp=mx1534x2048&ctp=s590x590&_nc_cat=110&_nc_map=urlgen_bucketless&ccb=1-7&_nc_sid=833d8c&_nc_eui2=AeFGyCKrIZe7l71PriaYmA2ZfD8tiC8svbF8Py2ILyy9sdLh8PAqeUm6ZUh-7knQeRR7NKBTAQUyLZzPcTRCvHOa&_nc_ohc=iohZUEB2QjwQ7kNvwFAPsui&_nc_oc=AdrJnfgOEdTxMszcXELhJF-QnWCyq_9fo0AykI4ORaR9BUP0D578dpZ_vPYkpXXdMIo&_nc_zt=23&_nc_ht=scontent.fcrk4-1.fna&_nc_gid=nGD5pPlT1YzOLGujB9DNCA&_nc_ss=7b2a8&oh=00_AQLbYNU4d2bRIgbquYEnXSv9GfvzVCZ3SWqLp-_eSCIFFg&oe=6AB35B0D",
        "min_price": 0, "max_price": 0, "base_price": 2500,
        "price_per_sqm": 25, "price_per_room": 0, "price_per_story": 0, "price_per_hour": 400,
        "use_sqm": 1, "use_room": 0, "use_story": 0, "use_hour": 1,
        "is_house_service": 1, "sort_order": 2,
    },
    {
        "name": "Kitchen Deep Clean",
        "description": "blank for now",
        "image": "https://scontent.fcrk4-1.fna.fbcdn.net/v/t39.30808-6/734455777_122109588855335674_5588808509546610090_n.jpg?stp=dst-jpg_tt6&cstp=mx1536x2048&ctp=s1536x2048&_nc_cat=106&_nc_map=urlgen_bucketless&ccb=1-7&_nc_sid=833d8c&_nc_eui2=AeGSq0HvO90vdaaQI-nnN-oiD_DbgXKfoD0P8NuBcp-gPYTkhxQWF5pNUUgGhNtbqvHabDP-APElEx4mw30JIo1D&_nc_ohc=HqKTUUCxjBcQ7kNvwFi0vL5&_nc_oc=AdrriWQcKLUwlpIXhaOR4UsiuNMs_dOVqbLBf3Vcbea42tQogQdGu8hkdz6bT1A9m3E&_nc_zt=23&_nc_ht=scontent.fcrk4-1.fna&_nc_gid=jRdN_OdV47VxqoHQggqumw&_nc_ss=7b2a8&oh=00_AQIJOnwldglkwMnG6ebdgnerkMkbHPC3BcIYCt8H0pSYcg&oe=6AB36283",
        "min_price": 0, "max_price": 0, "base_price": 2000,
        "price_per_sqm": 20, "price_per_room": 5, "price_per_story": 0, "price_per_hour": 0,
        "use_sqm": 1, "use_room": 1, "use_story": 0, "use_hour": 0,
        "is_house_service": 1, "sort_order": 3,
    },
    {
        "name": "Move Out Cleaning",
        "description": "blank for now",
        "image": "https://scontent.fcrk4-2.fna.fbcdn.net/v/t39.30808-6/734367586_122109588087335674_3083039879112732913_n.jpg?stp=dst-jpg_tt6&cstp=mx1536x2048&ctp=s590x590&_nc_cat=104&_nc_map=urlgen_bucketless&ccb=1-7&_nc_sid=833d8c&_nc_eui2=AeGJSAfHy1vVvidNoNzkb_T2OOsqOQWNJ-g46yo5BY0n6An4ZYfSnLcy0CMxyfVZfslOhohojAnixzjqF0AGV7m4&_nc_ohc=2wNtNyOzjQEQ7kNvwETfypo&_nc_oc=Adp9_tOjd1a4w9ibxHqZwb1_tTTlQ--K4CuMZoMZKc8sXzXN5Hx5E94laY9wX68O5Y4&_nc_zt=23&_nc_ht=scontent.fcrk4-2.fna&_nc_gid=fAmYWAhzAwNWcRafdF8Fzw&_nc_ss=7b2a8&oh=00_AQJvqwNZAkm5no1bzUJoUiRdVZXC4xfeGeZ9XcGrI0CbZQ&oe=6AB32E69",
        "min_price": 0, "max_price": 0, "base_price": 3000,
        "price_per_sqm": 30, "price_per_room": 0, "price_per_story": 0, "price_per_hour": 500,
        "use_sqm": 1, "use_room": 0, "use_story": 0, "use_hour": 1,
        "is_house_service": 1, "sort_order": 4,
    },
    {
        "name": "Glass Deep Clean",
        "description": "blank for now",
        "image": "https://scontent.fcrk2-2.fna.fbcdn.net/v/t39.30808-6/779392383_122119294221335674_488641587495305391_n.jpg?stp=cp6_dst-jpg_tt6&cstp=mx1536x2048&ctp=s1536x2048&_nc_cat=104&_nc_map=urlgen_bucketless&ccb=1-7&_nc_sid=833d8c&_nc_eui2=AeEvYCTlHnjuuXjiuDi0N-4ZnV4nGLspSNudXicYuylI22Im968fOXCE3gLQenvkrqtFs0g9YmRld0VvF2JxuCLs&_nc_ohc=Soj5bd4kYW0Q7kNvwFTvRcK&_nc_oc=Adpw7cmEEMIwXvJlc1iiKkE0FqUUZGlL6elYA8J2wC5o724jXSOlE5uuHdfB9xZG8D0&_nc_zt=23&_nc_ht=scontent.fcrk2-2.fna&_nc_gid=ZjEAaV4Z-aFEPLOvIg1log&_nc_ss=7b2a8&oh=00_AQJsh7TVsCjlU3xyT9akzj40nr8-aP4RR6gB-dNtIoQFgg&oe=6AB34805",
        "min_price": 0, "max_price": 0, "base_price": 3000,
        "price_per_sqm": 30, "price_per_room": 0, "price_per_story": 0, "price_per_hour": 500,
        "use_sqm": 1, "use_room": 0, "use_story": 0, "use_hour": 1,
        "is_house_service": 1, "sort_order": 5,
    },
    
    # --- Non-house services (is_house_service = 0) ---
    # These do NOT ask for house details; they are priced per hour of work.
    {
        "name": "Couch Cleaning",
        "description": "blank for now",
        "image": "https://scontent.fcrk8-1.fna.fbcdn.net/v/t39.30808-6/791890172_122122011477335674_2715949529703167382_n.jpg?stp=cp6_dst-jpg_tt6&cstp=mx1536x2048&ctp=s590x590&_nc_cat=109&_nc_map=urlgen_bucketless&ccb=1-7&_nc_sid=833d8c&_nc_eui2=AeGQyevERu1Fai7mK2wmkpZeRJ5TAgXSBj5EnlMCBdIGPqQVTTIFam5yI5riI0XWzG69yZC98FcRC_MiUOJLYRHu&_nc_ohc=V2APJCBs3nIQ7kNvwHPflku&_nc_oc=Adp18Ru9zElu4iWFoLs2IT5qNDLkFV55AYM-o9pGlEc4LUY3tF9aC4LOdhjw4zMSf_A&_nc_zt=23&_nc_ht=scontent.fcrk8-1.fna&_nc_gid=_XYWqfJmPDU332ERNXPxow&_nc_ss=7b2a8&oh=00_AQK_xiEzGIVHfZBZ7NSSgjfOYs2HyuzgBEYQjXU1GwJg4w&oe=6AB34751",
        "min_price": 0, "max_price": 0, "base_price": 1200,
        "price_per_sqm": 0, "price_per_room": 0, "price_per_story": 0, "price_per_hour": 300,
        "use_sqm": 0, "use_room": 0, "use_story": 0, "use_hour": 1,
        "is_house_service": 0, "sort_order": 6,
    },
    {
        "name": "Mattress Cleaning",
        "description": "blank for now",
        "image": "https://scontent.fcrk4-2.fna.fbcdn.net/v/t39.30808-6/760472217_122115262437335674_417348215138882339_n.jpg?stp=dst-jpg_tt6&cstp=mx1534x2048&ctp=s1534x2048&_nc_cat=101&_nc_map=urlgen_bucketless&ccb=1-7&_nc_sid=833d8c&_nc_eui2=AeH9z38_NYorm8Qn-p1DocO_Tze9SRlK4FxPN71JGUrgXOrxPCkg5XDM49YDQrrtlYXJVRDWjgvH_OZLuHYfTOH4&_nc_ohc=sFBt-TLAYmAQ7kNvwGXFKEO&_nc_oc=AdpeTL5V5TfcsnyqUsTE6amb8jGAU7R6fb5lOUKPSphEFnGlLqiFgf3X0J74_ktBs-c&_nc_zt=23&_nc_ht=scontent.fcrk4-2.fna&_nc_gid=uREKI4p_inKE5PvO26acXg&_nc_ss=7b2a8&oh=00_AQInhTwMo0jGVSnE7kWju706bIcboPjbko8pVkZ1cVTbLQ&oe=6AB3450A",
        "min_price": 0, "max_price": 0, "base_price": 900,
        "price_per_sqm": 0, "price_per_room": 0, "price_per_story": 0, "price_per_hour": 300,
        "use_sqm": 0, "use_room": 0, "use_story": 0, "use_hour": 1,
        "is_house_service": 0, "sort_order": 7,
    },
    {
        "name": "Carpet Cleaning",
        "description": "blank for now",
        "image": "https://scontent.fcrk2-3.fna.fbcdn.net/v/t39.30808-6/811501624_122124164991335674_6604854363957535733_n.jpg?stp=dst-jpg_tt6&cstp=mx1536x2048&ctp=s590x590&_nc_cat=103&_nc_map=urlgen_bucketless&ccb=1-7&_nc_sid=833d8c&_nc_eui2=AeHCgSZbkqh3y1KDU_3QL7OjjBbBXI37HSOMFsFcjfsdI18hjSqdekm-QAw3U9JbAWqHHvYZs9zxLkrbrFtQtAIy&_nc_ohc=gpobMUo2keUQ7kNvwHsesKa&_nc_oc=Ado1mqi8mZF39SP4QzE8Z0lM9Q9TZczjeYepm9-Htq_MExgsvFFnWdZuP5ebYsoqqB0&_nc_zt=23&_nc_ht=scontent.fcrk2-3.fna&_nc_gid=qHMkr-2wNGkkhnXGto8RrQ&_nc_ss=7b2a8&oh=00_AQLfyuMO1twwerMGaNXK92QQT9zMKM1Qjbdf_41MJxE87g&oe=6AB35F2B",
        "min_price": 0, "max_price": 0, "base_price": 1000,
        "price_per_sqm": 0, "price_per_room": 0, "price_per_story": 0, "price_per_hour": 350,
        "use_sqm": 0, "use_room": 0, "use_story": 0, "use_hour": 1,
        "is_house_service": 0, "sort_order": 8,
    },
    
]

DEFAULT_PROJECTS = [
    {
        "title": "Post Construction Cleaning",
        "description": "blank for now",
        "image": "https://scontent.fcrk4-1.fna.fbcdn.net/v/t39.30808-6/762331744_122116206567335674_4548940264414191538_n.jpg?stp=dst-jpg_tt6&cstp=mx1536x2048&ctp=s1536x2048&_nc_cat=110&_nc_map=urlgen_bucketless&ccb=1-7&_nc_sid=833d8c&_nc_eui2=AeHkniWltsWOJHQq4C8l-fQunaQXEwku9JSdpBcTCS70lC-wDq0ceoDX0x9TTYx1n9oN3IaW5lABYylcrIeXMCy5&_nc_ohc=uUZ_nvQhydMQ7kNvwEeqGVj&_nc_oc=AdpwKaS1KfvcDVtYGqyg-KH1Ns_oKCCDVNFklGOweBXFMCPCMxDLSnMS-HKNAjdeihU&_nc_zt=23&_nc_ht=scontent.fcrk4-1.fna&_nc_gid=Slbjd0apr5KIWMYxYTe3pQ&_nc_ss=7b2a8&oh=00_AQJ2wAYyrYA_vS9uaH0Zx9ALutdv-772FaXlUo69Z2RtVw&oe=6AB346B6", "sort_order": 1,
    },
    {
        "title": "Appartment Deep Clean",
        "description": "blank for now",
        "image": "https://scontent.fcrk4-1.fna.fbcdn.net/v/t39.30808-6/760343492_122115783309335674_6914114099330741156_n.jpg?stp=dst-jpg_tt6&cstp=mx1534x2048&ctp=s1534x2048&_nc_cat=106&_nc_map=urlgen_bucketless&ccb=1-7&_nc_sid=833d8c&_nc_eui2=AeG56L6CwIU4DObAyNP9MtPo1wDK60NWulnXAMrrQ1a6WezEMnM2CMvEtN-sW11rqyiLYcH_uEDwh7BJPJ-Ct-Q3&_nc_ohc=oQeKUUTaqi8Q7kNvwFz-_fw&_nc_oc=Adqf_0a77T26bIds7LNi6h63fxqwIxeUKBFFMVrYQb3EYFnWrOCW8FkbmyJYE7n4OIw&_nc_zt=23&_nc_ht=scontent.fcrk4-1.fna&_nc_gid=5FxlvFosYiMpfkmEAZ2nwg&_nc_ss=7b2a8&oh=00_AQJonatPYYXx8T4i7_n8hF9s7LRrqiDqbvAX9qmf4TWZsw&oe=6AB3473E", "sort_order": 2,
    },
    {
        "title": "Mattress Deep Clean",
        "description": "blank for now",
        "image": "https://scontent.fcrk4-1.fna.fbcdn.net/v/t39.30808-6/758964171_122115262953335674_5160818172419425604_n.jpg?stp=cp6_dst-jpg_tt6&cstp=mx1536x2048&ctp=s1536x2048&_nc_cat=107&_nc_map=urlgen_bucketless&ccb=1-7&_nc_sid=833d8c&_nc_eui2=AeENc3NWgKYNy7enOOYChZn2iBARmGETLl6IEBGYYRMuXs9jNunWmgnghskEgTA70wxpDb2tcTv26A_H5MR_eKPC&_nc_ohc=ElLJrMVG2WgQ7kNvwFZ4Fne&_nc_oc=AdpxjKqpyhIvLLsvx2fj90zM4ilGkuv-cQm8BNcBAljwKW2p7oqr7Myv9C31wH6rhlM&_nc_zt=23&_nc_ht=scontent.fcrk4-1.fna&_nc_gid=TIB9zgQlegb-BaJvEo_lpg&_nc_ss=7b2a8&oh=00_AQKqdtABur0AqJkCA4Sq8puaAXOQv6Os2jBg-9D9N0H8WA&oe=6AB3600A", "sort_order": 3,
    },
]

# ---------------------------------------------------------------------------
# The in-memory "tables"
# ---------------------------------------------------------------------------
_lock = threading.RLock()

_users: dict[int, dict] = {}
_services: dict[int, dict] = {}
_projects: dict[int, dict] = {}
_bookings: dict[int, dict] = {}
_reviews: dict[int, dict] = {}
_password_resets: dict[int, dict] = {}
_token_blocklist: set[str] = set()
_site_content: dict = {}

_counters = {
    "users": 1,
    "services": 1,
    "projects": 1,
    "bookings": 1,
    "reviews": 1,
    "password_resets": 1,
}
_seeded = False


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------
def _now() -> str:
    """Timestamp in the same format the old SQLite default produced."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _next_id(table: str) -> int:
    value = _counters[table]
    _counters[table] = value + 1
    return value


def _copy(row):
    """Return a deep copy so callers can never mutate stored state by accident."""
    return copy.deepcopy(row) if row is not None else None


def _copy_all(rows):
    return [copy.deepcopy(r) for r in rows]


# ---------------------------------------------------------------------------
# Seeding
# ---------------------------------------------------------------------------
def init_store() -> None:
    """Seed the demo data. Safe to call more than once."""
    global _seeded
    with _lock:
        if _seeded:
            return
        _seeded = True

        _site_content.clear()
        _site_content.update(copy.deepcopy(DEFAULT_SITE))
        _site_content["updated_at"] = _now()

        for svc in DEFAULT_SERVICES:
            sid = _next_id("services")
            _services[sid] = {"id": sid, **copy.deepcopy(svc)}

        for proj in DEFAULT_PROJECTS:
            pid = _next_id("projects")
            _projects[pid] = {"id": pid, **copy.deepcopy(proj)}

        # --- Sample admin account -------------------------------------------
        admin_id = _next_id("users")
        _users[admin_id] = {
            "id": admin_id,
            "first_name": "Admin",
            "last_name": "Owner",
            "phone": "09170000000",
            "email": SAMPLE_ADMIN_EMAIL,
            "password_hash": hash_password(SAMPLE_ADMIN_PASSWORD),
            "role": "admin",
            "municipality": "City of San Fernando",
            "barangay": "San Agustin",
            "address": None,
            "profile_pic": None,
            "created_at": _now(),
        }

        # --- Sample customer account ----------------------------------------
        customer_id = _next_id("users")
        _users[customer_id] = {
            "id": customer_id,
            "first_name": "Maria",
            "last_name": "Santos",
            "phone": "09171234567",
            "email": SAMPLE_CUSTOMER_EMAIL,
            "password_hash": hash_password(SAMPLE_CUSTOMER_PASSWORD),
            "role": "user",
            "municipality": "City of San Fernando",
            "barangay": "Alasas",
            "address": None,
            "profile_pic": None,
            "created_at": _now(),
        }

        # --- A couple of sample bookings for that customer ------------------
        # One completed (so the Reviews page can be tried straight away) and one
        # still pending. These are demo rows; the admin can edit or the whole
        # lot disappears on restart.
        deep_clean = _find_service_by_name("Home Deep Cleaning")
        couch = _find_service_by_name("Couch Cleaning")

        if deep_clean:
            bid = _next_id("bookings")
            _bookings[bid] = {
                "id": bid,
                "user_id": customer_id,
                "service_id": deep_clean["id"],
                "service_name": deep_clean["name"],
                "service_ids": [deep_clean["id"]],
                "service_names": [deep_clean["name"]],
                "floor_area_sqm": 80,
                "rooms": 3,
                "stories": 2,
                "schedule_date": "2026-08-20",
                "municipality": "City of San Fernando",
                "barang": "Alasas",
                "notes": "Please pay extra attention to the kitchen. (Sample booking)",
                "status": "completed",
                "payment_status": "paid",
                "downpayment": 0,
                "price": 5000,
                "created_at": _now(),
            }
            # A sample review on that completed booking.
            rid = _next_id("reviews")
            _reviews[rid] = {
                "id": rid,
                "booking_id": bid,
                "user_id": customer_id,
                "rating": 5,
                "comment": "The team was on time and the house looked brand new. Highly recommended!",
                "admin_reply": "Thank you so much, Maria! See you next time.",
                "created_at": _now(),
            }

        if couch:
            bid = _next_id("bookings")
            _bookings[bid] = {
                "id": bid,
                "user_id": customer_id,
                "service_id": couch["id"],
                "service_name": couch["name"],
                "service_ids": [couch["id"]],
                "service_names": [couch["name"]],
                "floor_area_sqm": None,
                "rooms": None,
                "stories": None,
                "schedule_date": "2026-12-15",
                "municipality": "City of San Fernando",
                "barang": "Alasas",
                "notes": "Two sofa sets in the living room. (Sample booking)",
                "status": "pending",
                "payment_status": "unpaid",
                "downpayment": 0,
                "price": 2100,
                "created_at": _now(),
            }


def _find_service_by_name(name: str):
    for svc in _services.values():
        if svc["name"] == name:
            return svc
    return None


# ---------------------------------------------------------------------------
# Password hashing (kept in this module so it works without any DB)
# ---------------------------------------------------------------------------
def hash_password(password: str) -> str:
    import bcrypt

    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def check_password(password: str, password_hash: str) -> bool:
    import bcrypt

    try:
        return bcrypt.checkpw(password.encode(), password_hash.encode())
    except (ValueError, TypeError):
        return False


# ---------------------------------------------------------------------------
# Demo accounts (served to the login page)
# ---------------------------------------------------------------------------
def demo_accounts() -> list[dict]:
    """The ready-to-use sample accounts, for the hint on the login page."""
    return [
        {
            "role": "user",
            "label": "Sample customer",
            "email": SAMPLE_CUSTOMER_EMAIL,
            "password": SAMPLE_CUSTOMER_PASSWORD,
            "note": "Has sample bookings and a review already.",
        },
        {
            "role": "admin",
            "label": "Sample admin",
            "email": SAMPLE_ADMIN_EMAIL,
            "password": SAMPLE_ADMIN_PASSWORD,
            "note": "Can manage bookings, services, reviews and site content.",
        },
    ]


# ===========================================================================
# USERS
# ===========================================================================
def get_user(uid: int):
    with _lock:
        return _copy(_users.get(int(uid)))


def find_user(identifier: str):
    """Find a user by email OR phone number (the login identifier)."""
    key = (identifier or "").strip().lower()
    if not key:
        return None
    with _lock:
        for user in _users.values():
            if (user["email"] or "").lower() == key or (user["phone"] or "").lower() == key:
                return _copy(user)
    return None


def list_users():
    with _lock:
        return _copy_all(_users.values())


def email_or_phone_taken(email: str, phone: str, exclude_id: int | None = None) -> bool:
    with _lock:
        for user in _users.values():
            if exclude_id is not None and user["id"] == int(exclude_id):
                continue
            if (user["email"] or "").lower() == (email or "").lower():
                return True
            if (user["phone"] or "") == (phone or ""):
                return True
    return False


def create_user(fields: dict) -> dict:
    with _lock:
        uid = _next_id("users")
        row = {
            "id": uid,
            "first_name": fields["first_name"],
            "last_name": fields["last_name"],
            "phone": fields["phone"],
            "email": (fields["email"] or "").lower(),
            "password_hash": fields["password_hash"],
            "role": fields.get("role", "user"),
            "municipality": fields.get("municipality"),
            "barangay": fields.get("barangay"),
            "address": fields.get("address"),
            "profile_pic": fields.get("profile_pic"),
            "created_at": _now(),
        }
        _users[uid] = row
        return _copy(row)


def update_user(uid: int, fields: dict):
    with _lock:
        row = _users.get(int(uid))
        if row is None:
            return None
        for key, value in fields.items():
            if key in row and key != "id":
                row[key] = value
        return _copy(row)


# ===========================================================================
# SERVICES
# ===========================================================================
def list_services():
    with _lock:
        rows = sorted(
            _services.values(),
            key=lambda s: (s.get("sort_order") or 0, s["id"]),
        )
        return _copy_all(rows)


def get_service(sid):
    try:
        sid = int(sid)
    except (TypeError, ValueError):
        return None
    with _lock:
        return _copy(_services.get(sid))


def create_service(fields: dict) -> dict:
    with _lock:
        sid = _next_id("services")
        row = {
            "id": sid,
            "name": fields["name"],
            "description": fields.get("description"),
            "image": fields.get("image"),
            "min_price": fields.get("min_price"),
            "max_price": fields.get("max_price"),
            "base_price": fields.get("base_price") or 0,
            "price_per_sqm": fields.get("price_per_sqm") or 0,
            "price_per_room": fields.get("price_per_room") or 0,
            "price_per_story": fields.get("price_per_story") or 0,
            "price_per_hour": fields.get("price_per_hour") or 0,
            "use_sqm": fields.get("use_sqm") or 0,
            "use_room": fields.get("use_room") or 0,
            "use_story": fields.get("use_story") or 0,
            "use_hour": fields.get("use_hour") or 0,
            "is_house_service": fields.get("is_house_service", 1),
            "sort_order": fields.get("sort_order") or 0,
        }
        _services[sid] = row
        return _copy(row)


def update_service(sid: int, fields: dict):
    with _lock:
        row = _services.get(int(sid))
        if row is None:
            return None
        for key, value in fields.items():
            if key in row and key != "id":
                row[key] = value
        return _copy(row)


def delete_service(sid: int) -> bool:
    with _lock:
        return _services.pop(int(sid), None) is not None


# ===========================================================================
# PROJECTS
# ===========================================================================
def list_projects():
    with _lock:
        rows = sorted(_projects.values(), key=lambda p: (p.get("sort_order") or 0, p["id"]))
        return _copy_all(rows)


def create_project(fields: dict) -> dict:
    with _lock:
        pid = _next_id("projects")
        row = {
            "id": pid,
            "title": fields["title"],
            "description": fields.get("description"),
            "image": fields.get("image"),
            "sort_order": fields.get("sort_order") or 0,
        }
        _projects[pid] = row
        return _copy(row)


def update_project(pid: int, fields: dict):
    with _lock:
        row = _projects.get(int(pid))
        if row is None:
            return None
        for key, value in fields.items():
            if key in row and key != "id":
                row[key] = value
        return _copy(row)


def delete_project(pid: int) -> bool:
    with _lock:
        return _projects.pop(int(pid), None) is not None


# ===========================================================================
# SITE CONTENT
# ===========================================================================
def get_site() -> dict:
    with _lock:
        return _copy(_site_content)


def update_site(fields: dict) -> dict:
    with _lock:
        for key, value in fields.items():
            if key in _site_content and key not in ("id",):
                _site_content[key] = value
        _site_content["updated_at"] = _now()
        return _copy(_site_content)


# ===========================================================================
# BOOKINGS
# ===========================================================================
def get_booking(bid: int):
    try:
        bid = int(bid)
    except (TypeError, ValueError):
        return None
    with _lock:
        return _copy(_bookings.get(bid))


def list_bookings_for_user(uid: int):
    with _lock:
        rows = [b for b in _bookings.values() if b["user_id"] == int(uid)]
        rows.sort(key=lambda b: b["schedule_date"], reverse=True)
        return _copy_all(rows)


def list_bookings_on_date(schedule_date: str):
    with _lock:
        return _copy_all([b for b in _bookings.values() if b["schedule_date"] == schedule_date])


def availability_by_date() -> dict:
    """Count of bookings per date, plus how many are secured by a downpayment."""
    with _lock:
        dates: dict[str, dict] = {}
        for booking in _bookings.values():
            entry = dates.setdefault(booking["schedule_date"], {"count": 0, "secured": 0})
            entry["count"] += 1
            if (booking.get("downpayment") or 0) > 0:
                entry["secured"] += 1
        return dates


def list_all_bookings():
    """Every booking, newest schedule first, joined with its customer details."""
    with _lock:
        rows = []
        for booking in _bookings.values():
            user = _users.get(booking["user_id"])
            row = copy.deepcopy(booking)
            row["customer_name"] = (
                f"{user['first_name']} {user['last_name']}" if user else "Unknown customer"
            )
            row["customer_phone"] = user["phone"] if user else None
            row["customer_email"] = user["email"] if user else None
            rows.append(row)
        rows.sort(key=lambda b: b["schedule_date"], reverse=True)
        return rows


def create_booking(fields: dict) -> dict:
    with _lock:
        bid = _next_id("bookings")
        row = {
            "id": bid,
            "user_id": fields["user_id"],
            "service_id": fields.get("service_id"),
            "service_name": fields.get("service_name"),
            "service_ids": list(fields.get("service_ids") or []),
            "service_names": list(fields.get("service_names") or []),
            "floor_area_sqm": fields.get("floor_area_sqm"),
            "rooms": fields.get("rooms"),
            "stories": fields.get("stories"),
            "schedule_date": fields["schedule_date"],
            "municipality": fields["municipality"],
            "barang": fields["barang"],
            "notes": fields.get("notes"),
            "status": fields.get("status", "pending"),
            "payment_status": fields.get("payment_status", "unpaid"),
            "downpayment": fields.get("downpayment") or 0,
            "price": fields.get("price") or 0,
            "created_at": _now(),
        }
        _bookings[bid] = row
        return _copy(row)


def update_booking(bid: int, fields: dict):
    with _lock:
        row = _bookings.get(int(bid))
        if row is None:
            return None
        for key, value in fields.items():
            if key in row and key != "id":
                row[key] = value
        return _copy(row)


def find_secured_booking(schedule_date: str, exclude_id: int | None = None):
    """A booking on this date that has already been secured by a downpayment."""
    with _lock:
        for booking in _bookings.values():
            if booking["schedule_date"] != schedule_date:
                continue
            if exclude_id is not None and booking["id"] == int(exclude_id):
                continue
            if (booking.get("downpayment") or 0) > 0:
                return _copy(booking)
    return None


# ===========================================================================
# REVIEWS
# ===========================================================================
def list_reviews(with_user: bool = False):
    """All reviews, newest first.

    With `with_user=True` each row also carries `user_name` (public shape) or,
    when `full_name=True` is used by the admin route, the customer's full name.
    """
    with _lock:
        rows = []
        for review in _reviews.values():
            row = copy.deepcopy(review)
            user = _users.get(review["user_id"])
            if with_user:
                if user:
                    row["user_name"] = f"{user['first_name']} {user['last_name'][0]}."
                    row["customer_name"] = f"{user['first_name']} {user['last_name']}"
                else:
                    row["user_name"] = "Unknown"
                    row["customer_name"] = "Unknown"
                booking = _bookings.get(review["booking_id"])
                row["service_name"] = booking["service_name"] if booking else None
                row["schedule_date"] = booking["schedule_date"] if booking else None
            rows.append(row)
        rows.sort(key=lambda r: r["created_at"], reverse=True)
        return rows


def get_review(rid: int):
    try:
        rid = int(rid)
    except (TypeError, ValueError):
        return None
    with _lock:
        return _copy(_reviews.get(rid))


def find_review_by_booking(booking_id: int):
    with _lock:
        for review in _reviews.values():
            if review["booking_id"] == int(booking_id):
                return _copy(review)
    return None


def create_review(fields: dict) -> dict:
    with _lock:
        rid = _next_id("reviews")
        row = {
            "id": rid,
            "booking_id": fields["booking_id"],
            "user_id": fields["user_id"],
            "rating": fields["rating"],
            "comment": fields.get("comment"),
            "admin_reply": fields.get("admin_reply"),
            "created_at": _now(),
        }
        _reviews[rid] = row
        return _copy(row)


def update_review(rid: int, fields: dict):
    with _lock:
        row = _reviews.get(int(rid))
        if row is None:
            return None
        for key, value in fields.items():
            if key in row and key != "id":
                row[key] = value
        return _copy(row)


# ===========================================================================
# PASSWORD RESETS
# ===========================================================================
def create_password_reset(user_id: int, token: str, expires_at: str) -> dict:
    with _lock:
        rid = _next_id("password_resets")
        row = {
            "id": rid,
            "user_id": user_id,
            "token": token,
            "expires_at": expires_at,
            "used": 0,
        }
        _password_resets[rid] = row
        return _copy(row)


def find_password_reset(token: str):
    with _lock:
        for row in _password_resets.values():
            if row["token"] == token and not row["used"]:
                return _copy(row)
    return None


def mark_password_reset_used(rid: int):
    with _lock:
        row = _password_resets.get(int(rid))
        if row is None:
            return None
        row["used"] = 1
        return _copy(row)


# ===========================================================================
# TOKEN BLOCKLIST (logout)
# ===========================================================================
def block_token(jti: str) -> None:
    with _lock:
        _token_blocklist.add(jti)


def is_token_blocked(jti: str) -> bool:
    with _lock:
        return jti in _token_blocklist


# ---------------------------------------------------------------------------
# Reset everything (used by the tests)
# ---------------------------------------------------------------------------
def reset_store() -> None:
    """Wipe every in-memory table and re-seed. Handy for tests."""
    global _seeded
    with _lock:
        for table in _users, _services, _projects, _bookings, _reviews, _password_resets:
            table.clear()
        _token_blocklist.clear()
        _site_content.clear()
        for key in _counters:
            _counters[key] = 1
        _seeded = False
    init_store()
