# TLS certificates

Drop your certificate files here when enabling the optional HTTPS proxy:

- `cert.pem` — leaf certificate, optionally concatenated with any intermediate chain
- `key.pem`  — matching private key

The files are mounted read-only into the Caddy container at `/certs/` and referenced by
`caddy/Caddyfile`.

## Quick self-signed cert for local testing

```bash
openssl req -x509 -newkey rsa:4096 -sha256 -days 365 -nodes \
    -keyout certs/key.pem -out certs/cert.pem \
    -subj "/CN=localhost" \
    -addext "subjectAltName=DNS:localhost,IP:127.0.0.1"
```

Then set `TLS_DOMAIN=localhost` in `docker-compose.yml` (already the default)
and browse to <https://localhost/> after `docker compose up --build` (accept
the self-signed warning).

## Cloudflare origin certificates

If you are fronting the instance with Cloudflare, generate an
[origin certificate](https://developers.cloudflare.com/ssl/origin-configuration/origin-ca/)
in the Cloudflare dashboard, save it as `cert.pem`, and save the private key as `key.pem`
here. Cloudflare will terminate the public TLS connection; Caddy only needs to serve a cert
that Cloudflare trusts between itself and your server.
