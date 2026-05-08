# Generative polygl0t Transformer

Flask + SQLite parody helpdesk for CTF finals.

## Features

- player-facing landing page with account-backed chat history;
- register/login flow where registration returns a generated password once;
- two-step submission flow (human queue or bot);
- human queue with atomic claiming and 90-second lease expiry;
- polygl0ts dashboard restricted to the seeded admin account;
- experimental Playwright bot that only visits same-origin chat URLs;
- English, French, Italian, German, and best-effort Romansh UI packs;
- Docker Compose wiring ready out of the box.

## Quick start

```bash
docker compose up --build
```

Then open <https://localhost/> and accept the self-signed certificate warning.

All tunables live inline at the top of `docker-compose.yml` under the
`x-challenge-env` anchor. Update them before shipping the challenge:

- `ADMIN_USERNAME` / `ADMIN_PASSWORD` — seeded admin account for the dashboard.
- `SECRET_KEY` — Flask session signing key.
- `BOT_INTERNAL_TOKEN` — shared secret between the app and the headless bot.
- `FLAG_COOKIE_NAME` / `FLAG` — cookie the bot plants on the chat page
  (`FLAG_COOKIE_NAME=flag` by default, `FLAG` is the actual flag value).
- `TLS_DOMAIN` — hostname served by Caddy.
- `BOT_VISIT_BASE_URL` — origin the bot uses when expanding relative chat
  paths. In Docker this should usually stay `http://app:8000`.

Caddy generates a self-signed cert on first boot (`tls internal` in
`source/caddy/Caddyfile`). To deploy with real certificates see
**Custom certificates** below.

## Accounts

- registration only asks for a username; the server returns a generated
  password once. Players must save that password themselves.
- the seeded admin account is controlled by `ADMIN_USERNAME` /
  `ADMIN_PASSWORD` in `docker-compose.yml`.
- after logging in as admin, open `/dashboard`.

## Custom certificates

1. Drop `cert.pem` and `key.pem` into `./source/certs/` (see
   `source/certs/README.md` for a Cloudflare origin-cert walkthrough or an
   OpenSSL self-signed example).
2. In `source/caddy/Caddyfile`, comment out `tls internal` and uncomment
   `tls /certs/cert.pem /certs/key.pem`.
3. In `docker-compose.yml`, set `TLS_DOMAIN` to the hostname on the cert.

Prefer automatic Let's Encrypt instead? Drop the `auto_https disable_certs`
directive from the Caddyfile and replace `tls internal` with
`tls you@example.com`. This requires public DNS pointing at the host and
working :80/:443 reachability for ACME http-01.

## Cloudflare deployment notes

- put the public hostname behind a proxied Cloudflare DNS record;
- set `TLS_DOMAIN` to that hostname;
- the app already trusts `CF-Connecting-IP` / `X-Forwarded-For` for rate
  limiting since it always runs behind the Caddy proxy;
- test the live site on the proxied hostname, not only locally.

## Local run without Docker

```bash
cd source
pip install -r requirements.txt
ADMIN_PASSWORD=admin \
gunicorn -c gunicorn.conf.py app:app
```

The bot worker only makes sense when running through Docker (it targets the
`app` service DNS name); for direct local runs, skip it.
