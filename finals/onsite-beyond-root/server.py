import base64
import io
import os
import json
import hmac
import hashlib
import secrets
import time
import urllib.error
import urllib.request
from pathlib import Path

from flask import Flask, abort, request
from PIL import Image

app = Flask(__name__)


def _get_image_path() -> Path:
    # Where we store the latest uploaded image (always saved as PNG).
    env_path = os.environ.get("IMAGE_PATH")
    if env_path:
        return Path(env_path)
    return Path(__file__).parent / "stored_image.png"


IMAGE_PATH = _get_image_path()

DEVICE_CONFIG_PATH = Path(__file__).parent / "device_config.json"

AUTH_NONCE_TTL_S = int(os.environ.get("DEVICE_AUTH_NONCE_TTL_S", "300"))
DEVICE_ID = os.environ.get("ESP32_DEVICE_ID", "esp32cam-01")
DEVICE_SECRET = os.environ.get("ESP32_AUTH_SECRET", "LAKE{lmao_this_is_a_key_not_a_flag}")
_used_nonces: dict[str, float] = {}


def _require_device_secret() -> str:
    if not DEVICE_SECRET:
        abort(500, "ESP32_AUTH_SECRET is not set on the web server")
    return DEVICE_SECRET


def _cleanup_seen_nonces(now: float) -> None:
    cutoff = now - AUTH_NONCE_TTL_S
    stale = [nonce for nonce, ts in _used_nonces.items() if ts < cutoff]
    for nonce in stale:
        _used_nonces.pop(nonce, None)


def _verify_device_request_auth() -> None:
    secret = _require_device_secret()
    device_id = (request.headers.get("X-Device-Id") or "").strip()
    nonce = (request.headers.get("X-Auth-Nonce") or "").strip()
    sig = (request.headers.get("X-Auth-Signature") or "").strip().lower()

    if not device_id or not nonce or not sig:
        abort(401, "Missing device authentication headers")
    if device_id != DEVICE_ID:
        abort(401, "Unknown device id")
    if len(sig) != 64:
        abort(401, "Invalid signature format")

    now = time.time()
    _cleanup_seen_nonces(now)
    nonce_key = f"{device_id}:{nonce}"
    if nonce_key in _used_nonces:
        abort(401, "Replay detected")

    msg = f"{request.method}\n{request.path}\n{nonce}\n{device_id}".encode("utf-8")
    expected = hmac.new(secret.encode("utf-8"), msg, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, sig):
        abort(401, "Invalid signature")

    _used_nonces[nonce_key] = now


def _load_device_config() -> dict:
    if not DEVICE_CONFIG_PATH.exists():
        return {
            "image_path": "/photo.jpg",
            "device_name": "esp32cam-01",
        }
    try:
        cfg = json.loads(DEVICE_CONFIG_PATH.read_text(encoding="utf-8"))
        if not isinstance(cfg, dict):
            raise ValueError("Invalid config JSON shape")
        cfg = {k: v for k, v in cfg.items() if k in ("image_path", "device_name")}
        if not (cfg.get("device_name") or "").strip():
            cfg["device_name"] = "esp32cam-01"
        return cfg
    except Exception:
        return {
            "image_path": "/photo.jpg",
            "device_name": "esp32cam-01",
        }


def _save_device_config(cfg: dict) -> None:
    DEVICE_CONFIG_PATH.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")

def _esp32_base_url() -> str:
    # Example: http://192.168.1.50
    return os.environ.get("ESP32_BASE_URL", "").rstrip("/")


def _esp32_url(path: str) -> str:
    base = _esp32_base_url()
    if not base:
        abort(500, "ESP32_BASE_URL is not set (example: http://192.168.1.50)")
    if not path.startswith("/"):
        path = "/" + path
    return base + path


def _http_json(method: str, url: str, payload: dict | None = None, timeout_s: int = 5):
    data = None
    headers = {"Accept": "application/json"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url=url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            raw = resp.read()
            ct = (resp.headers.get("Content-Type") or "").lower()
            if "application/json" in ct:
                return resp.status, json.loads(raw.decode("utf-8"))
            return resp.status, raw.decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        abort(e.code, f"ESP32 error: {body}")
    except Exception as e:
        abort(502, f"Failed to reach ESP32 at {url}: {e}")


@app.route("/upload", methods=["POST"])
def upload():
    """
    Accept a multipart form upload with field name `file` and convert it to PNG.
    """
    _verify_device_request_auth()

    if "file" not in request.files:
        abort(400, "Missing multipart field: file")

    uploaded = request.files["file"]
    if not uploaded or not uploaded.filename:
        abort(400, "No file provided")

    raw = uploaded.read()
    if not raw:
        abort(400, "Empty upload")

    try:
        with open(IMAGE_PATH, "wb") as f:
          f.write(raw)
    except Exception as e:
        abort(400, f"Could not decode/convert image: {e}")

    return {"ok": True}, 200


@app.route("/view", methods=["GET"])
def view():
    """
    Simple GUI page that embeds the latest stored PNG (data URI).
    """
    if not IMAGE_PATH.exists():
        html = """
        <html>
          <head><meta name="viewport" content="width=device-width, initial-scale=1"></head>
          <body style="font-family: Arial; text-align:center; padding: 30px;">
            <h2>No image uploaded yet</h2>
            <p>Send a PNG (or JPEG/etc) to <code>/upload</code>.</p>
          </body>
        </html>
        """
        return html, 200
        
    with open(IMAGE_PATH, "rb") as f:
        raw = f.read()
        b64 = base64.b64encode(raw).decode("ascii")

    cfg = _load_device_config()
    device_name = (cfg.get("device_name") or "esp32cam-01")
    html = f"""
    <html>
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
          body {{ text-align:center; font-family: Arial; }}
          img {{ width: 90%; max-width: 800px; height: auto; border: 1px solid #ddd; }}
        </style>
      </head>
      <body>
        <h2>Latest Upload</h2>
        <p>
          <button onclick="location.reload()">Refresh</button>
        </p>
        <img src="data:image/png;base64,{b64}" alt="Latest image">
      </body>
    </html>
    """
    return html, 200


@app.route("/", methods=["GET"])
def home():
    html = """
    <html>
      <head><meta name="viewport" content="width=device-width, initial-scale=1"></head>
      <body style="font-family: Arial; padding: 20px;">
        <h2>Get to see Beyond Root here!</h2>
        <ul>
          <li><a href="/view">View latest sight</a></li>
          <li><a href="/device-config-ui">Edit config</a></li>
        </ul>
      </body>
    </html>
    """
    return html, 200


@app.route("/device-config", methods=["GET"])
def device_config_get():
    """
    Config that the ESP32 periodically pulls from this server.
    """
    return _load_device_config(), 200


@app.route("/device-config/device", methods=["GET"])
def device_config_get_for_device():
    """
    Device-authenticated config endpoint for ESP32.
    """
    _verify_device_request_auth()
    return _load_device_config(), 200


@app.route("/device-config", methods=["POST"])
def device_config_set():
    body = request.get_json(silent=True) or {}
    if not isinstance(body, dict):
        abort(400, "Invalid JSON payload")
    current = _load_device_config()
    image_path = (body.get("image_path", current.get("image_path", "/photo.jpg")) or "").strip()
    device_name = (body.get("device_name", current.get("device_name", "esp32cam-01")) or "").strip()
    if not image_path:
        abort(400, "Missing image_path")
    if not device_name:
        abort(400, "Missing device_name")
    cfg = {"image_path": image_path, "device_name": device_name}
    _save_device_config(cfg)
    return {"ok": True, "config": cfg}, 200


@app.route("/device-config-ui", methods=["GET"])
def device_config_ui():
    html = """
    <html>
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
          body { font-family: Arial; margin: 16px; }
          input { width: 100%; box-sizing: border-box; padding: 10px; }
          .row { margin: 10px 0; }
          pre { background: #111; color: #eee; padding: 10px; border-radius: 6px; white-space: pre-wrap; }
          button { margin-right: 8px; }
        </style>
      </head>
      <body>
        <h2>Device config (stored on /config.json on the camera)</h2>
        <p>will take a while to update</p>
        <div class="row">
          <label>device_name</label>
          <input id="device_name" placeholder="esp32cam-01" />
        </div>
        <div class="row">
          <label>image_type</label>
          <select id="image_path">
            <option value="/photo.jpg">UXGA</option>
            <option value="/photo_svga.jpg">SVGA</option>
          </select>
     
        </div>
        <div class="row">
          <button onclick="loadCfg()">Reload</button>
          <button onclick="saveCfg()">Save</button>
          <button onclick="location.href='/view'">Back to image</button>
        </div>
        <pre id="status"></pre>

        <script>
          async function loadCfg(){
            const r = await fetch('/device-config');
            const j = await r.json();
            document.getElementById('device_name').value = j.device_name || '';
            document.getElementById('image_path').value = j.image_path || '';
            document.getElementById('status').textContent = 'Loaded.';
          }

          async function saveCfg(){
            const payload = {
              device_name: document.getElementById('device_name').value.trim(),
              image_path: document.getElementById('image_path').value.trim()
            };
            const r = await fetch('/device-config', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(payload)
            });
            const j = await r.json();
            document.getElementById('status').textContent = "Updated.";
          }

          loadCfg();
        </script>
      </body>
    </html>
    """
    return html, 200


def main():
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "9999"))
    # Disable Flask reloader to avoid issues during challenge testing.
    app.run(host=host, port=port, debug=False, use_reloader=False)


if __name__ == "__main__":
    main()

