from flask_sqlalchemy import SQLAlchemy

from .clock import utcnow

db = SQLAlchemy()


class Site(db.Model):
    __tablename__ = "sites"
    id = db.Column(db.Integer, primary_key=True)
    domain = db.Column(db.String(128), unique=True)
    created_at = db.Column(db.DateTime, default=utcnow)


class PageView(db.Model):
    __tablename__ = "page_views"
    id = db.Column(db.Integer, primary_key=True)
    site_id = db.Column(db.Integer, db.ForeignKey("sites.id"), index=True)
    path = db.Column(db.String(256), default="/")
    referrer = db.Column(db.String(256), default="")
    ip_hash = db.Column(db.String(64), default="")
    ua = db.Column(db.String(256), default="")
    country = db.Column(db.String(8), default="")
    at = db.Column(db.DateTime, default=utcnow)


class DailyAgg(db.Model):
    __tablename__ = "daily_aggs"
    id = db.Column(db.Integer, primary_key=True)
    site_id = db.Column(db.Integer, db.ForeignKey("sites.id"))
    date = db.Column(db.String(10), default="")
    views = db.Column(db.Integer, default=0)
    visitors = db.Column(db.Integer, default=0)
