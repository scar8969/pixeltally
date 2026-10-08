== curl ==
# curl -i "http://127.0.0.1:5000/pixel/myapp?path=/docs&ref=reddit"   (1x1 gif, no Set-Cookie)
# GET  /api/sites
# POST /api/sites  {"domain":"myapp"}
# GET  /api/sites/1/stats?days=7

== session plan ==
# Session 1: tracker (pixel + ip_hash + no cookies) → tests
# Session 2: agg (rollup/visitors/pages/referrers) → tests
# Session 3: web dashboard + embed.js → screenshots → README → CI/Docker/Pages → tag
