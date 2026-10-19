"""Command line client for privacy-analytics.

    python cli.py --help
    python cli.py sites
    python cli.py add example.com
    python cli.py stats 1 --days 7
    python cli.py pixel example.com --path /docs --ref https://news.example.com

Talks to a running instance (see README: python wsgi.py).
"""

import argparse
import json
import os
import urllib.error
import urllib.parse
import urllib.request

DEFAULT_BASE = os.environ.get("ANALYTICS_URL", "http://127.0.0.1:8000")


def _call(method, path, data=None, headers=None, base=None):
    req = urllib.request.Request(
        (base or DEFAULT_BASE).rstrip("/") + path, data=data, method=method, headers=headers or {}
    )
    with urllib.request.urlopen(req) as r:
        return r.status, dict(r.headers), r.read()


def cmd_sites(args):
    try:
        status, headers, data = _call("GET", "/api/sites", base=args.base)
    except urllib.error.HTTPError as exc:
        print("request failed: HTTP %s" % exc.code)
        return 1
    sites = json.loads(data.decode()).get("sites", [])
    print("HTTP %s - %d site(s)" % (status, len(sites)))
    if not sites:
        print("(none registered yet - try: python cli.py add example.com)")
        return 0
    print("%-6s %-30s %10s" % ("id", "domain", "views"))
    for s in sites:
        print("%-6s %-30s %10s" % (s["id"], s["domain"][:30], s["views"]))
    return 0


def cmd_add(args):
    payload = json.dumps({"domain": args.domain}).encode()
    try:
        status, headers, data = _call(
            "POST", "/api/sites", payload, {"Content-Type": "application/json"}, args.base
        )
    except urllib.error.HTTPError as exc:
        print("request failed: HTTP %s %s" % (exc.code, exc.read().decode("utf-8", "replace")))
        return 1
    print("HTTP %s %s" % (status, data.decode().strip()))
    return 0


def cmd_stats(args):
    try:
        status, headers, data = _call(
            "GET", "/api/sites/%d/stats?days=%d" % (args.site_id, args.days), base=args.base
        )
    except urllib.error.HTTPError as exc:
        print("request failed: HTTP %s" % exc.code)
        return 1
    payload = json.loads(data.decode())
    print("HTTP %s - site %d, last %d day(s)" % (status, args.site_id, args.days))
    print("series:    %d day(s)" % len(payload.get("series", [])))
    for row in payload.get("series", []):
        print("  %s  views=%-5s visitors=%s" % (row["date"], row["views"], row["visitors"]))
    print("top pages:")
    for path, count in payload.get("pages", []):
        print("  %-34s %s" % (path, count))
    print("referrers:")
    for ref, pct in payload.get("referrers", {}).items():
        print("  %-34s %s%%" % (ref, pct))
    return 0


def cmd_pixel(args):
    q = urllib.parse.urlencode({"path": args.path, "ref": args.ref})
    try:
        status, headers, data = _call("GET", "/pixel/%s?%s" % (args.domain, q), base=args.base)
    except urllib.error.HTTPError as exc:
        print("pixel failed: HTTP %s (unknown domain?)" % exc.code)
        return 1
    print(
        "HTTP %s %s %d bytes cache-control=%s set-cookie=%s"
        % (
            status,
            headers.get("Content-Type", ""),
            len(data),
            headers.get("Cache-Control", ""),
            headers.get("Set-Cookie", "none"),
        )
    )
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(
        prog="analytics", description="privacy-analytics command line client"
    )
    p.add_argument("--base", default=DEFAULT_BASE, help="base URL of a running instance")
    sub = p.add_subparsers(dest="cmd")

    s = sub.add_parser("sites", help="list registered sites")
    s.set_defaults(func=cmd_sites)

    a = sub.add_parser("add", help="register a domain")
    a.add_argument("domain")
    a.set_defaults(func=cmd_add)

    t = sub.add_parser("stats", help="show rollup / top pages / referrers for a site id")
    t.add_argument("site_id", type=int)
    t.add_argument("--days", type=int, default=7)
    t.set_defaults(func=cmd_stats)

    x = sub.add_parser("pixel", help="fire the tracking pixel once and report what came back")
    x.add_argument("domain")
    x.add_argument("--path", default="/")
    x.add_argument("--ref", default="")
    x.set_defaults(func=cmd_pixel)

    args = p.parse_args(argv)
    if getattr(args, "func", None) is None:
        p.print_help()
        return 0
    return args.func(args)


if __name__ == "__main__":  # pragma: no cover - manual entry point
    raise SystemExit(main())
