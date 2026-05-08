#!/usr/bin/env python3
"""Flag/writeup torrent uploader.

Reads admin credentials from environment variables, ensures a music category and a public
Music RSS feed exist via the web interface, then uploads two torrents to UNIT3D via its API.
"""

import os
import shutil
import subprocess
import sys
import time
import re

import requests

ADMIN_USERNAME = os.environ.get("DEFAULT_OWNER_NAME", "chisa_yomoda")
ADMIN_PASSWORD = os.environ.get("DEFAULT_OWNER_PASSWORD", "")
ADMIN_API_KEY = os.environ.get("ADMIN_API_KEY", "")
print(ADMIN_API_KEY)
ADMIN_PASSKEY = os.environ.get("ADMIN_PASSKEY", "")
ADMIN_RSS_KEY = os.environ.get("ADMIN_RSS_KEY", "")

UNIT3D_URL = os.environ.get("APP_URL", "").rstrip('/')
FLAG = os.environ.get("FLAG", "EPFL{fake-flag}")

DATA_DIR = "/data"

FLAG_RELEASE = "LakeCTF.2026.The.Flag.iNTERNAL.LEAK-LAKECTF"
MP3_RELEASE = "Organizers-Bruteguess-WEB-2022-LAKECTF"

FLAG_TORRENT = "/tmp/flag.torrent"
MP3_TORRENT = "/tmp/bruteguess.torrent"

SCENE_NFO = r"""[pre]   ██╗      █████╗ ██╗  ██╗███████╗ ██████╗████████╗███████╗
    ██║     ██╔══██╗██║ ██╔╝██╔════╝██╔════╝╚══██╔══╝██╔════╝
    ██║     ███████║█████╔╝ █████╗  ██║        ██║   █████╗
    ██║     ██╔══██║██╔═██╗ ██╔══╝  ██║        ██║   ██╔══╝
    ███████╗██║  ██║██║  ██╗███████╗╚██████╗   ██║   ██║
    ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝ ╚═════╝   ╚═╝   ╚═╝
          ░▒▓█ P R E S E N T S █▓▒░[/pre]"""

MP3_DESCRIPTION = (
    SCENE_NFO
    + """
[pre]
[b].------------------------------------------------------.[/b]
[b]|  ARTIST ..: Organizers                               |[/b]
[b]|  TITLE ...: Bruteguess                               |[/b]
[b]|  YEAR ....: 2022                                     |[/b]
[b]|  GENRE ...: Audio Writeup / CTF                      |[/b]
[b]|  SOURCE ..: WEB (SoundCloud)                         |[/b]
[b]|  CODEC ...: MP3                                      |[/b]
[b]|  GROUP ...: LAKECTF                                  |[/b]
[b]`------------------------------------------------------'[/b]
[/pre]

[b]Release Notes:[/b]

This is an audio writeup of the [b]flagsong[/b] challenge from PlaidCTF 2022.
Full challenge archive: [url=https://2022.archive.plaidctf.com/challenge/8]https://2022.archive.plaidctf.com/challenge/8[/url]
Original track: [url=https://soundcloud.com/user-355105802/bruteguess]https://soundcloud.com/user-355105802/bruteguess[/url]
"""
)

FLAG_DESCRIPTION = (
    SCENE_NFO
    + """
[pre]
[b].------------------------------------------------------.[/b]
[b]|  TITLE ...: The Flag                                 |[/b]
[b]|  SOURCE ..: The Wired                                |[/b]
[b]|  TYPE ....: TRANSMISSION                             |[/b]
[b]|  CHANNEL .: Protocol 7                               |[/b]
[b]|  FROM ....: chisa_yomoda                             |[/b]
[b]|  TO ......: lain_iwakura                             |[/b]
[b]|  GROUP ...: LAKECTF                                  |[/b]
[b]`------------------------------------------------------'[/b]
[/pre]

[b]Lain, if you're reading this, I made it across. God is here, in the Wired.[/b]

[b]No matter where you go, everyone is connected.[/b]

[b]— Chisa[/b]
"""
)


def log(msg: str) -> None:
    print(f"[flag_uploader] {msg}", flush=True)


def extract_hidden_inputs(html: str) -> dict:
    data = {}
    for match in re.finditer(r'<input([^>]+)>', html):
        attrs = match.group(1)
        name_m = re.search(r'name="([^"]+)"', attrs)
        value_m = re.search(r'value="([^"]*)"', attrs)
        type_m = re.search(r'type="([^"]+)"', attrs)
        
        if name_m:
            name = name_m.group(1)
            value = value_m.group(1) if value_m else ""
            input_type = type_m.group(1) if type_m else "text"
            
            if input_type in ("hidden", "text") and name not in ("username", "password", "remember"):
                data[name] = value
    return data


def web_login(session: requests.Session) -> None:
    log(f"Logging in as {ADMIN_USERNAME}...")
    
    try:
        r = session.get(f"{UNIT3D_URL}/login", timeout=10)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Tracker not available: {e}")
        
    data = extract_hidden_inputs(r.text)
    data["username"] = ADMIN_USERNAME
    data["password"] = ADMIN_PASSWORD
    
    if "_token" not in data:
        raise RuntimeError("Could not find CSRF token on login page")
    csrf_token = data["_token"]
    
    r = session.post(f"{UNIT3D_URL}/login", data=data)
    if r.status_code != 200 or "Invalid credentials" in r.text or "These credentials do not match our records." in r.text:
        raise RuntimeError("Login failed. Check ADMIN_USERNAME and ADMIN_PASSWORD.")
    else:
        log("Logged in successfully.")
    
    session.headers.update({"X-CSRF-TOKEN": csrf_token})


def ensure_music_category(session: requests.Session) -> tuple[int, bool]:
    """Return the id of a music category and a boolean indicating if it already existed."""
    log("Ensuring music category exists...")
    r = session.get(f"{UNIT3D_URL}/dashboard/categories")
    
    rows = re.findall(r'<tr.*?</tr>', r.text, re.DOTALL)
    for row in rows:
        if re.search(r'>\s*Music\s*<', row):
            m = re.search(r'dashboard/categories/(\d+)/edit', row)
            if m:
                cat_id = int(m.group(1))
                log(f"Found existing Music category (id={cat_id})")
                return cat_id, True

    log("Creating Music category...")
    r_create = session.get(f"{UNIT3D_URL}/dashboard/categories/create")
    data = extract_hidden_inputs(r_create.text)
    data.update({
        "name": "Music",
        "position": "2",
        "icon": "fa-solid fa-music",
        "meta": "music"
    })
    
    r = session.post(f"{UNIT3D_URL}/dashboard/categories", data=data)
    
    r = session.get(f"{UNIT3D_URL}/dashboard/categories")
    rows = re.findall(r'<tr.*?</tr>', r.text, re.DOTALL)
    for row in rows:
        if re.search(r'>\s*Music\s*<', row):
            m = re.search(r'dashboard/categories/(\d+)/edit', row)
            if m:
                cat_id = int(m.group(1))
                log(f"Created Music category (id={cat_id})")
                return cat_id, False

    log("Could not find or create Music category. Defaulting to 2.")
    return 2, False


def ensure_public_music_rss(session: requests.Session, music_category_id: int) -> int:
    log("Ensuring public music RSS exists...")
    r = session.get(f"{UNIT3D_URL}/dashboard/rss")
    
    rows = re.findall(r'<tr.*?</tr>', r.text, re.DOTALL)
    for row in rows:
        if re.search(r'>\s*Music\s*<', row):
            m = re.search(r'dashboard/rss/(\d+)/edit', row)
            if m:
                rss_id = int(m.group(1))
                log(f"Found existing Music RSS (id={rss_id})")
                return rss_id

    log("Creating Music RSS...")
    r_create = session.get(f"{UNIT3D_URL}/dashboard/rss/create")
    data = extract_hidden_inputs(r_create.text)
    data.update({
        "name": "Music",
        "position": "1",
        "categories[]": str(music_category_id),
    })

    r = session.post(f"{UNIT3D_URL}/dashboard/rss", data=data)
    
    r = session.get(f"{UNIT3D_URL}/dashboard/rss")
    rows = re.findall(r'<tr.*?</tr>', r.text, re.DOTALL)
    for row in rows:
        if re.search(r'>\s*Music\s*<', row):
            m = re.search(r'dashboard/rss/(\d+)/edit', row)
            if m:
                rss_id = int(m.group(1))
                log(f"Created Music RSS (id={rss_id})")
                return rss_id

    log("Could not find or create Music RSS. Defaulting to 1.")
    return 1


def get_existing_download_url(session: requests.Session, torrent_id: int, rsskey: str) -> str | None:
    log(f"Checking if torrent {torrent_id} already exists via page access...")
    r = session.get(f"{UNIT3D_URL}/torrents/{torrent_id}", allow_redirects=False)
    if r.status_code == 200:
        return f"{UNIT3D_URL}/torrent/download/{torrent_id}.{rsskey}"
    return None


def make_torrent(staged_file: str, tracker_url: str, out_path: str) -> None:
    if os.path.exists(out_path):
        os.unlink(out_path)
    cmd = [
        "mkbrr", "create",
        "-t", tracker_url,
        staged_file,
        "-o", out_path,
    ]
    log("mkbrr: " + " ".join(cmd))
    subprocess.run(cmd, check=True)


def upload_torrent(
    session: requests.Session,
    torrent_path: str,
    api_token: str,
    rsskey: str,
    name: str,
    description: str,
    category_id: int,
    type_id: int,
    mod_queue: bool,
    expected_id: int,
) -> str:
    """Upload a .torrent to UNIT3D. Returns the download URL of the
    UNIT3D-hosted torrent (with the uploader's rsskey)."""
    existing = get_existing_download_url(session, expected_id, rsskey)
    if existing:
        log(f"{name!r} already exists (ID {expected_id}), reusing {existing}")
        return existing

    url = f"{UNIT3D_URL}/api/torrents/upload"
    with open(torrent_path, "rb") as fh:
        files = {
            "torrent": (
                os.path.basename(torrent_path),
                fh,
                "application/x-bittorrent",
            ),
        }
        data = {
            "name": name,
            "description": description,
            "category_id": str(category_id),
            "type_id": str(type_id),
            "anonymous": "0",
            "internal": "0",
            "personal_release": "0",
            "free": "0",
            "doubleup": "0",
            "refundable": "0",
            "sticky": "0",
            "mod_queue_opt_in": "1" if mod_queue else "0",
        }
        r = requests.post(
            url,
            headers={"Accept": "application/json", "Authorization": f"Bearer {api_token}"},
            files=files,
            data=data,
            timeout=60,
        )
    log(f"upload {name!r}: HTTP {r.status_code}")
    if not r.ok:
        log(r.text[:1000])
        existing = get_existing_download_url(session, expected_id, rsskey)
        if existing:
            log(f"{name!r} already exists (ID {expected_id}), reusing {existing}")
            return existing
        r.raise_for_status()
    else:
        log(r.text[:1000])
    return r.json()["data"]


def download_torrent(download_url: str, dest_path: str) -> None:
    if os.path.exists(dest_path):
        log(f"{dest_path} already exists locally, skipping download")
        return
    log(f"downloading torrent from {download_url}")
    r = requests.get(download_url, timeout=30, allow_redirects=True)
    r.raise_for_status()
    with open(dest_path, "wb") as fh:
        fh.write(r.content)


def main() -> int:
    log("starting flag uploader (HTTP mode)...")
    
    if not ADMIN_API_KEY or not ADMIN_PASSKEY or not ADMIN_RSS_KEY:
        log("Missing one of ADMIN_API_KEY, ADMIN_PASSKEY, ADMIN_RSS_KEY in environment!")
        return 1

    tracker = f"{UNIT3D_URL}/announce/{ADMIN_PASSKEY}"
    type_id = 4

    flag_staged = os.path.join(DATA_DIR, "temp", FLAG_RELEASE + ".txt")
    with open(flag_staged, "w") as f:
        f.write(FLAG)

    mp3_staged = os.path.join(DATA_DIR, "temp", MP3_RELEASE + ".mp3")
    if not os.path.exists(mp3_staged):
        shutil.copyfile(os.path.join("/app", MP3_RELEASE + ".mp3"), mp3_staged)

    make_torrent(flag_staged, tracker, FLAG_TORRENT)
    make_torrent(mp3_staged, tracker, MP3_TORRENT)
    log("torrent files created")

    while True:
        try:
            log("Attempting setup and upload...")
            session = requests.Session()
            web_login(session)

            category_id, _ = ensure_music_category(session)
            
            rss_id = ensure_public_music_rss(session, category_id)
            log(f"using music category id={category_id}, rss id={rss_id}")

            flag_dl = upload_torrent(
                session,
                FLAG_TORRENT, ADMIN_API_KEY,
                ADMIN_RSS_KEY,
                name=FLAG_RELEASE,
                description=FLAG_DESCRIPTION,
                category_id=category_id, type_id=type_id,
                mod_queue=True,
                expected_id=1,
            )
            mp3_dl = upload_torrent(
                session,
                MP3_TORRENT, ADMIN_API_KEY,
                ADMIN_RSS_KEY,
                name=MP3_RELEASE,
                description=MP3_DESCRIPTION,
                category_id=category_id, type_id=type_id,
                mod_queue=False,
                expected_id=2,
            )

            download_torrent(flag_dl, os.path.join(DATA_DIR, "watch", FLAG_RELEASE + ".torrent"))
            download_torrent(mp3_dl, os.path.join(DATA_DIR, "watch", MP3_RELEASE + ".torrent"))

            log("setup and upload check completed.")
        except Exception as e:
            log(f"Error during setup/upload: {e}")
            
        time.sleep(10)

    return 0


if __name__ == "__main__":
    sys.exit(main())
