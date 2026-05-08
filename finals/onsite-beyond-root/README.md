## Flask Web Server

Endpoints:
- `POST /upload` - multipart form upload with field name `file` (PNG/JPEG/etc accepted; server converts to PNG).
- `GET /view` - simple page that embeds the latest stored PNG.
- `GET /device-config` - returns the server-stored JSON config that the ESP32 should pull
- `POST /device-config` - updates the server-stored JSON config
- `GET /device-config-ui` - small GUI to edit the server-stored config
- `GET /esp32/config` - proxy to ESP32-CAM `GET /config` (requires `ESP32_BASE_URL`)
- `POST /esp32/config` - proxy to ESP32-CAM `POST /config` (requires `ESP32_BASE_URL`)
- `GET /esp32/config-ui` - small GUI to edit ESP32 config via Flask

### Run

```bash
pip install -r requirements.txt
python server.py
```

Optional environment variables:
- `HOST` (default `0.0.0.0`)
- `PORT` (default `5000`)
- `IMAGE_PATH` (default `stored_image.png` next to `server.py`)
- `ESP32_BASE_URL` (example `http://192.168.1.50`)

