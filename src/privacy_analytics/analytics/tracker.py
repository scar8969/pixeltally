import os

import hashlib

def ip_hash(ip):
    return hashlib.sha256(f"{_SALT}:{ip}".encode()).hexdigest()[:16]

def record(site_id, path, referrer, ip, ua):
    from .geo import country
    from ..models import PageView, db

    db.session.add(PageView(site_id=site_id, path=path[:256], referrer=referrer[:256],
                            ip_hash=ip_hash(ip), ua=ua[:256], country=country(ip)))
    db.session.commit()

_SALT = os.environ.get("ANALYTICS_SALT", "dev-salt")
