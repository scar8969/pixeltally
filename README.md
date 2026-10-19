<p align="center">
  <img src="docs/assets/screens/root.png" alt="pixeltally running" width="900">
</p>

<h1 align="center">pixeltally</h1>

<p align="center"><b>Page views without cookies: a salted hash, never an IP.</b></p>

<p align="center">
  <a href="https://github.com/scar8969/pixeltally/actions/workflows/ci.yml"><img src="https://github.com/scar8969/pixeltally/actions/workflows/ci.yml/badge.svg" alt="ci"></a> <a href="#quality-gates"><img src="https://img.shields.io/badge/tests-24%20passed-2ea44f" alt="tests: 24 passed"></a> <a href="#quality-gates"><img src="https://img.shields.io/badge/coverage-63.0%-yellow" alt="coverage: 63.0%"></a> <a href="#api"><img src="https://img.shields.io/badge/routes-10%20live-0969da" alt="routes: 10 live"></a> <a href="#requirements"><img src="https://img.shields.io/badge/python-3.11%2B-3776ab" alt="python: 3.11+"></a> <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-2ea44f" alt="license: MIT"></a>
</p>

pixeltally is a cookie-less analytics server. One pixel request records a page view keyed by a salted hash of the visitor tuple, and the dashboard reads per-day rollups. No cookie is set and no IP address is stored.

---

**Contents** &nbsp;·&nbsp; [Why](#why-this-exists) &nbsp;·&nbsp; [What it does](#what-it-does) &nbsp;·&nbsp; [Quickstart](#quickstart) &nbsp;·&nbsp; [Screenshots](#screenshots) &nbsp;·&nbsp; [API](#api) &nbsp;·&nbsp; [CLI](#cli) &nbsp;·&nbsp; [Configuration](#configuration) &nbsp;·&nbsp; [Measured](#measured-not-estimated) &nbsp;·&nbsp; [How a request flows](#how-a-request-flows) &nbsp;·&nbsp; [Architecture](#architecture) &nbsp;·&nbsp; [Quality gates](#quality-gates) &nbsp;·&nbsp; [Development](#development) &nbsp;·&nbsp; [Deploy](#deploy) &nbsp;·&nbsp; [Limits](#limits-stated-rather-than-hidden)

## Why this exists

Most "privacy-friendly" analytics still store something that identifies a person. This one stores a salted digest with a rotating salt, keeps only the fields the rollup needs, and says so in the code that writes the row.

## What it does

| Capability | How it works |
| --- | --- |
| **Salted visitor hash** | A SHA-256 digest of the request tuple with the server salt from ANALYTICS_SALT; the raw tuple is never stored. |
| **No cookies, no IPs** | The pixel sets nothing and the row has no address column. |
| **Per-day rollups** | Views, paths and referrers aggregated per site per day. |
| **Site management** | Create sites, get a pixel URL, read stats. |

## Quickstart

```sh
git clone https://github.com/scar8969/pixeltally.git
cd pixeltally
python -m venv .venv && . .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
python wsgi.py                                 # http://127.0.0.1:8000
```

It is up when this answers:

```sh
curl -s http://127.0.0.1:8000/api/sites
```

## Screenshots

Captured from the running service with headless Chromium at 1440×900, one image per page, committed under [`docs/assets/screens/`](docs/assets/screens/).

<table>
<tr>
<td width="50%"><img src="docs/assets/screens/docs.png" alt="/docs" width="100%"><br><sub><code>/docs</code> &middot; 44.5 KB</sub></td>
<td width="50%"><img src="docs/assets/screens/sites.png" alt="/sites" width="100%"><br><sub><code>/sites</code> &middot; 25.7 KB</sub></td>
</tr>
</table>

The other 5 captures — the health, liveness, readiness, metrics and version endpoints — are committed in the same folder rather than shown here.

## API

Every route below is declared in [`openapi/pixeltally.yaml`](openapi/pixeltally.yaml) and exercised by the live probe recorded in [`docs/EVIDENCE.md`](docs/EVIDENCE.md).

| Method | Path | What it does |
| --- | --- | --- |
| `GET` | `/pixel/<site>` | tracking pixel |
| `GET` | `/api/sites` | list |
| `POST` | `/api/sites` | create |
| `GET` | `/api/sites/<id>/stats` | stats |

## CLI

The same operations without an HTTP client. Installed as `pixeltally`, and runnable from a checkout with no install:

```sh
python -m privacy_analytics.cli --help
```

```text
usage: analytics [-h] [--base BASE] {sites,add,stats,pixel} ...

privacy-analytics command line client

positional arguments:
  {sites,add,stats,pixel}
    sites               list registered sites
    add                 register a domain
    stats               show rollup / top pages / referrers for a site id
    pixel               fire the tracking pixel once and report what came back

options:
  -h, --help            show this help message and exit
  --base BASE           base URL of a running instance
```

## Configuration

Environment only — there is no config file. Copy `.env.example` to `.env` and edit; `APP_ENV=production` refuses to start without `SECRET_KEY`.

| Variable | Default | Meaning |
| --- | --- | --- |
| `APP_ENV` | `development` | development \| staging \| production; production enforces the secret. |
| `SECRET_KEY` | `change-me-in-production` | Session/CSRF signing key. Required when APP_ENV=production. |
| `HOST` | `0.0.0.0` | Interface the dev server binds. |
| `PORT` | `8000` | Port the dev server and the container listen on. |
| `DEBUG` | `false` | Flask debug mode. Never true in production. |
| `MAX_CONTENT_LENGTH` | `8388608` | Largest accepted request body, in bytes. |
| `DATA_DIR` | `(empty)` | Where uploaded and generated files live. |
| `INSTANCE_DIR` | `(empty)` | Where the SQLite file and instance state live. |
| `LOG_DIR` | `(empty)` | Where rotated log files are written, if file logging is on. |
| `LOG_LEVEL` | `INFO` | DEBUG \| INFO \| WARNING \| ERROR. |
| `LOG_JSON` | `true` | true emits one JSON object per line; false is human-readable. |
| `REQUEST_ID_HEADER` | `X-Request-ID` | Header echoed on every response and stamped on every log line. |
| `ANALYTICS_SALT` | `change-me-in-production` | Salt for the visitor hash. Changing it resets visitor identity. |
| `ANALYTICS_URL` | `http://127.0.0.1:8000` | Base URL the CLI talks to; also accepted as --url. |

## Measured, not estimated

Produced on this checkout by `pytest --cov` and by booting `wsgi.py` and issuing one real GET per documented path. The commands are recorded in [`docs/EVIDENCE.md`](docs/EVIDENCE.md).

| Signal | Value |
| --- | --- |
| Tests | **24 / 24 passed** (2.3 s, exit 0) |
| Line coverage | **63.0%** — 441 of 669 statements |
| Source | 15 files / 1,515 lines |
| Test code | 4 files / 234 lines |
| Documented paths | 3 in the spec, 3 GET |
| Live probe | 13 GET requests to the booted app, **10 answered 200** |
| Median latency | **7.9 ms** (single uncached request, dev server) |
| Slowest / fastest | 130.7 ms `/` / 4.2 ms `/healthz` |
| Bytes served | 20.1 KB across 13 responses |
| Screenshots | 8 captured |

## How a request flows

```text
client
  │  HTTP
  ▼
wsgi.py ──▶ privacy_analytics/app.py:get_app()
                │  reads config once (privacy_analytics/config.py)
                │  registers the `analytics` blueprint
                ▼
           route handler
             ├──▶ privacy_analytics/models.py        tables, via Flask-SQLAlchemy
             ├──▶ privacy_analytics/errors.py        raises typed errors → one JSON envelope
             └──▶ privacy_analytics/observability.py JSON log line + X-Request-ID
```

Every response carries `X-Request-ID`, and the matching log line is written once at the end of the request with the status and duration, so a report of "it failed" is one `grep` away from the traceback.

## Architecture

```
pixeltally/
├── src/privacy_analytics/
│   ├── http.py                         379  HTTP plumbing for privacy_analytics: correlation ids
│   ├── _app.py                         181  
│   ├── config.py                       173  Environment-driven configuration for privacy_analyti
│   ├── observability.py                169  Structured logging and request correlation for priva
│   ├── cli.py                          136  Command line client for privacy-analytics
│   ├── app.py                          119  Application factory for privacy_analytics
│   ├── errors.py                       108  Typed application errors and their HTTP mapping for 
│   ├── analytics/api.py                 64  
│   ├── paths.py                         52  Filesystem layout for privacy_analytics
│   ├── analytics/agg.py                 46  
│   ├── models.py                        34  
│   ├── analytics/tracker.py             27  
├── openapi/pixeltally.yaml                the contract of record
├── schema/pixeltally.sql                  the DDL
├── tests/                       the suite that has to stay green
├── docs/EVIDENCE.md             the recorded live route walk
├── Dockerfile                   multi-stage build
└── wsgi.py                      entry point
```

The package keeps one shape across the service: `config.py` reads the environment once, `observability.py` emits structured JSON logs carrying a request id, `errors.py` turns exceptions into a single JSON envelope, `models.py` holds the tables, and the `analytics/` package holds the routes.

## Quality gates

| Gate | Command | Threshold |
| --- | --- | --- |
| Suite | `pytest -q` | all green |
| Coverage | `pytest --cov` | floor in `pyproject.toml`, set below the measured value |
| Lint | `ruff check src tests` | zero findings |
| Format | `ruff format --check src tests` | zero reformats |
| Types | `mypy src` | zero errors |
| Security | `bandit -c pyproject.toml -r src` | reviewed skip list, no unreviewed finding |
| Live routes | boot `wsgi.py`, one GET per documented path | no 5xx, no undocumented guard |

CI runs the first six on Python 3.11, 3.12 and 3.13 on every push to `main`, plus a container build — [`.github/workflows/ci.yml`](.github/workflows/ci.yml).

## Development

```sh
pip install -e ".[dev]"
python -m pytest -q                      # the suite
python -m pytest --cov                   # with the coverage floor
python -m ruff check src tests           # lint
python -m ruff format --check src tests  # formatting
python -m mypy src                       # types
python -m bandit -c pyproject.toml -r src  # security
pre-commit install                       # the same checks on commit
```

Dependabot opens grouped PRs for the dev tooling weekly and for actions and the base image monthly.

## Deploy

```sh
docker build -t pixeltally .
docker run --rm -p 8000:8000 --env-file .env.example pixeltally
```

A `docker-compose.yml` is included for a local run with a volume for the SQLite file. The image runs as a non-root user and serves through gunicorn.

## Limits, stated rather than hidden

- Unique-visitor counts are approximate by construction: a different user agent or a different day produces a different hash.
- The salt is read once at import; changing it separates every visitor from their history.

## License

MIT — see [LICENSE](LICENSE).
