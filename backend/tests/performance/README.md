Load test profiles are defined in `load_profiles.json`.

Examples:
- Expected load: `locust --headless -u 10 -r 2 -t 2m`
- 10x load: `locust --headless -u 100 -r 10 -t 5m`
- 50x load: `locust --headless -u 500 -r 50 -t 10m`
- 100x load: `locust --headless -u 1000 -r 100 -t 15m`

Set target host with `LOCUST_HOST`, e.g. `LOCUST_HOST=http://localhost:8000`.
