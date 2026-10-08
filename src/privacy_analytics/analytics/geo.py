def country(ip):
    try:
        from geoip2.database import Reader
        with Reader("GeoLite2-Country.mmdb") as r:
            return r.country(ip).country.iso_code or "unknown"
    except Exception:
        return "unknown"
