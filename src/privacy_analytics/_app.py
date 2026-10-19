import os
from datetime import timedelta
from typing import Any

from flask import Flask, flash, jsonify, redirect, render_template, request, url_for

from . import paths
from .analytics.agg import referrers, rollup, top_pages
from .analytics.api import bp
from .analytics.tracker import record
from .clock import utcnow
from .models import PageView, Site, db

paths.INSTANCE_DIR.mkdir(parents=True, exist_ok=True)


def build_app():
    """Build the application: configuration, database, then routes."""
    app = Flask(
        __name__, template_folder=str(paths.TEMPLATES_DIR), instance_path=str(paths.INSTANCE_DIR)
    )
    app.secret_key = os.environ.get("SECRET_KEY", "analytics-dev-secret")
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + str(paths.INSTANCE_DIR / "analytics.db")
    db.init_app(app)
    with app.app_context():
        db.create_all()
    app.register_blueprint(bp)

    DAYS = 14

    @app.context_processor
    def _ctx():
        return {"app_name": "\U0001f4ca analytics"}

    def _window(site_id=None, days=DAYS):
        since = utcnow() - timedelta(days=days)
        q = PageView.query.filter(PageView.at >= since)
        if site_id is not None:
            q = q.filter(PageView.site_id == site_id)
        views = q.all()
        return views, len({v.ip_hash for v in views})

    def _all_series(days=DAYS):
        since = utcnow() - timedelta(days=days)
        buckets: dict[str, Any] = {}
        for v in PageView.query.filter(PageView.at >= since).all():
            key = v.at.date().isoformat()
            b = buckets.setdefault(key, {"views": 0, "visitors": set()})
            b["views"] += 1
            b["visitors"].add(v.ip_hash)
        return [
            {"date": k, "views": b["views"], "visitors": len(b["visitors"])}
            for k, b in sorted(buckets.items())
        ]

    def _site_rows(days=DAYS):
        rows = []
        for s in Site.query.order_by(Site.id).all():
            views, _ = _window(s.id, days)
            rows.append(
                {
                    "site": s,
                    "views": PageView.query.filter_by(site_id=s.id).count(),
                    "window": len(views),
                    "pixel": url_for("analytics.pixel", site=s.domain),
                }
            )
        return rows

    def _bucket_max(series):
        return max([s["views"] for s in series] + [1])

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok", "service": "privacy-analytics", "version": "0.1.0"})

    @app.get("/")
    def index():
        series = _all_series(DAYS)
        views, visitors = _window(None, DAYS)
        countries = {v.country for v in PageView.query.all() if v.country}
        return render_template(
            "index.html",
            days=DAYS,
            site_count=Site.query.count(),
            view_total=PageView.query.count(),
            window_views=len(views),
            window_visitors=visitors,
            country_count=len(countries),
            series=series,
            series_max=_bucket_max(series),
            rows=_site_rows(DAYS),
            salt_source="ANALYTICS_SALT env var"
            if os.environ.get("ANALYTICS_SALT")
            else "dev-salt default (set ANALYTICS_SALT in production)",
        )

    @app.route("/sites", methods=["GET", "POST"])
    def sites_page():
        if request.method == "POST":
            domain = (request.form.get("domain") or "").strip().lower()
            if not domain:
                flash("A domain is required.", "err")
            elif Site.query.filter_by(domain=domain).first():
                flash("Site %s is already registered." % domain, "err")
            else:
                s = Site(domain=domain)
                db.session.add(s)
                db.session.commit()
                flash(
                    "Registered %s — pixel is live at %s"
                    % (domain, url_for("analytics.pixel", site=domain)),
                    "ok",
                )
                return redirect(url_for("site_detail", sid=s.id))
        return render_template("sites.html", rows=_site_rows(DAYS), days=DAYS)

    @app.get("/sites/<int:sid>")
    def site_detail(sid):
        site = Site.query.get_or_404(sid)
        series = rollup(sid, DAYS)
        pages = top_pages(sid, DAYS, 10)
        refs = referrers(sid, DAYS)
        views, visitors = _window(sid, DAYS)
        pages_total = sum(c for _, c in pages) or 1
        return render_template(
            "site.html",
            site=site,
            days=DAYS,
            total_views=PageView.query.filter_by(site_id=sid).count(),
            window_views=len(views),
            window_visitors=visitors,
            series=series,
            series_max=_bucket_max(series),
            pages=pages,
            pages_max=max([c for _, c in pages] + [1]),
            pages_total=pages_total,
            referrers=refs,
            pixel_absolute=url_for("analytics.pixel", site=site.domain, _external=True),
            recent=PageView.query.filter_by(site_id=sid)
            .order_by(PageView.id.desc())
            .limit(25)
            .all(),
        )

    @app.post("/sites/<int:sid>/pixel")
    def site_pixel_test(sid):
        site = Site.query.get_or_404(sid)
        record(
            site.id,
            (request.form.get("path") or "/").strip() or "/",
            (request.form.get("ref") or "").strip(),
            request.remote_addr or "",
            request.headers.get("User-Agent", ""),
        )
        flash("Recorded one page view for %s." % site.domain, "ok")
        return redirect(url_for("site_detail", sid=site.id))

    @app.get("/docs")
    def api_docs():
        rules = []
        for r in sorted(app.url_map.iter_rules(), key=lambda r: str(r)):
            methods = ",".join(
                sorted(
                    m
                    for m in (r.methods or set())
                    if m in {"GET", "POST", "PUT", "PATCH", "DELETE"}
                )
            )
            if methods:
                rules.append({"methods": methods, "rule": str(r), "endpoint": r.endpoint})
        return render_template("api_docs.html", rules=rules)

    if __name__ == "__main__":
        app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8000")))

    return app


app = build_app()
