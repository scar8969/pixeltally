from datetime import datetime, timedelta

def rollup(site_id, days=30):
    from ..models import PageView, db

    since = datetime.utcnow() - timedelta(days=days)
    views = PageView.query.filter(PageView.site_id == site_id, PageView.at >= since).all()
    series = {}
    for v in views:
        d = v.at.date().isoformat()
        series.setdefault(d, {"views": 0, "visitors": set()})
        series[d]["views"] += 1
        series[d]["visitors"].add(v.ip_hash)
    return [{"date": d, "views": s["views"], "visitors": len(s["visitors"])}
            for d, s in sorted(series.items())]

def top_pages(site_id, days=7, limit=10):
    from ..models import PageView
    from datetime import timedelta
    since = datetime.utcnow() - timedelta(days=days)
    pages = {}
    for v in PageView.query.filter(PageView.site_id == site_id, PageView.at >= since).all():
        pages[v.path] = pages.get(v.path, 0) + 1
    return sorted(pages.items(), key=lambda kv: -kv[1])[:limit]

def referrers(site_id, days=7):
    from ..models import PageView
    from datetime import timedelta
    since = datetime.utcnow() - timedelta(days=days)
    refs = {}
    for v in PageView.query.filter(PageView.site_id == site_id, PageView.at >= since).all():
        r = v.referrer or "direct"
        refs[r] = refs.get(r, 0) + 1
    total = sum(refs.values()) or 1
    return {k: round(v / total * 100, 1) for k, v in refs.items()}
