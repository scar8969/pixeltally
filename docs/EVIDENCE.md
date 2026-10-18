# Evidence

Every claim below comes from a command that was actually run against this
exact checkout. Nothing here is inferred from the source alone.

## Commands

```sh
# from the project directory, with _tools and _tools/_vendor on PYTHONPATH
python -m pytest -q -p hosttmp_proj tests/
python -m compileall -q src
```

## Recorded results

| check | result |
| --- | --- |
| compileall | exit 0 |
| pytest | -- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html |
| pytest_exit_code | 0 |
| recorded_at | 2026-10-08 |
| routes_ok | 13 |
| routes_probed | 13 |

## HTTP surface

One real GET per rule in the assembled URL map, through Flask's test
client. `ok` includes 404 on a templated path: an empty database has
no such resource, and 404 is the honest answer for that.

| method | path | rule | status | bytes | note |
| --- | --- | --- | --- | --- | --- |
| GET | `/` | `/` | 200 | 5520 | ok |
| GET | `/api/health` | `/api/health` | 200 | 64 | ok |
| GET | `/api/sites` | `/api/sites` | 200 | 13 | ok |
| GET | `/api/sites/demo/stats` | `/api/sites/<int:sid>/stats` | 404 | 51 | ok |
| GET | `/docs` | `/docs` | 200 | 8191 | ok |
| GET | `/healthz` | `/healthz` | 200 | 64 | ok |
| GET | `/livez` | `/livez` | 200 | 19 | ok |
| GET | `/metrics` | `/metrics` | 200 | 305 | ok |
| GET | `/pixel/demo` | `/pixel/<site>` | 404 | 0 | ok |
| GET | `/readyz` | `/readyz` | 200 | 31 | ok |
| GET | `/sites` | `/sites` | 200 | 5078 | ok |
| GET | `/sites/demo` | `/sites/<int:sid>` | 404 | 207 | ok |
| GET | `/version` | `/version` | 200 | 979 | ok |

## Operational endpoints

`/healthz` answered **200**:

```
{"service":"privacy_analytics","status":"ok","version":"0.1.0"}
```

`/livez` answered **200**:

```
{"status":"alive"}
```

`/readyz` answered **200**:

```
{"checks":[],"status":"ready"}
```

`/metrics` answered **200**:

```
# TYPE http_requests_total counter
http_requests_total{method="GET",status="200"} 4
# TYPE http_request_duration_seconds_sum counter
http_request_duration_seconds_sum{method="GET"} 0.0334783
http_requests_total{method="GET",status="404"} 1
# TYPE process_uptime_seconds gauge
process_uptime_seconds 0.545
```

`/version` answered **200**:

```
{"config":{"app_name":"privacy_analytics","data_dir":".\\var","database_configured":false,"debug":false,"env":"development","host":"0.0.0.0","legacy_env_present":[],"log_json":true,"log_level":"INFO","port":8000,"secret_key_configured":false},"paths":{"data_dir":"b11_
```

## Headers observed on /healthz

| header | value |
| --- | --- |
| X-Request-ID | 5f982d034a854effab0d4fcaaefb9384 |
| X-Content-Type-Options | nosniff |
| X-Frame-Options | DENY |
| Referrer-Policy | no-referrer |
| Cross-Origin-Opener-Policy | same-origin |
| Permissions-Policy | geolocation=(), microphone=(), camera=() |
| Content-Type | application/json |

## What this file does not claim

- No browser screenshot: this host denies the Chromium sandbox the renderer
  needs, so the HTTP surface is evidenced with recorded status codes instead.
- No network access: the suite is hermetic and contacts no remote host.
- No container run: the Dockerfile is reviewed, not executed, because no
  container runtime is reachable from this host.
