"""Public site content, services, projects, demo accounts and Pampanga data."""
from flask import Blueprint, jsonify

import store
from helpers import service_dict
from pampanga import PAMPANGA

bp = Blueprint("site", __name__, url_prefix="/api")


@bp.get("/site")
def get_site():
    return jsonify(
        {
            "site": store.get_site(),
            "services": [service_dict(s) for s in store.list_services()],
            "projects": store.list_projects(),
        }
    )


@bp.get("/demo-accounts")
def demo_accounts():
    """The ready-to-use sample logins shown on the Login page.

    This is a demo build, so the credentials are returned openly on purpose --
    there is nothing private in here and it keeps the app usable with no setup.
    """
    return jsonify({"accounts": store.demo_accounts()})


@bp.get("/pampanga")
def pampanga():
    return jsonify(PAMPANGA)
