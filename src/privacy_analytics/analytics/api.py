from flask import Blueprint, Response, jsonify, request

from ..models import PageView, Site, db
from .agg import referrers, rollup, top_pages
from .tracker import record

bp = Blueprint("analytics", __name__)

GIF = b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b"


@bp.get("/pixel/<site>")
def pixel(site):
    s = Site.query.filter_by(domain=site).first()
    if not s:
        return Response(status=404)
    record(
        s.id,
        request.args.get("path", "/"),
        request.args.get("ref", ""),
        request.remote_addr or "",
        request.headers.get("User-Agent", ""),
    )
    resp = Response(GIF, mimetype="image/gif")
    resp.headers["Cache-Control"] = "no-store"
    return resp  # NO Set-Cookie


@bp.get("/api/sites")
def sites():
    return jsonify(
        {
            "sites": [
                {
                    "id": s.id,
                    "domain": s.domain,
                    "views": PageView.query.filter_by(site_id=s.id).count(),
                }
                for s in Site.query.all()
            ]
        }
    )


@bp.post("/api/sites")
def add_site():
    d = request.get_json(force=True, silent=True) or {}
    s = Site(domain=d.get("domain", ""))
    db.session.add(s)
    db.session.commit()
    return jsonify({"id": s.id})


@bp.get("/api/sites/<int:sid>/stats")
def stats(sid):
    days = request.args.get("days", 7, type=int)
    return jsonify(
        {
            "series": rollup(sid, days),
            "pages": top_pages(sid, days),
            "referrers": referrers(sid, days),
        }
    )
