const SENSITIVE_FIELDS = ["magnet_uri", "tracker", "hash"];

function redact(torrent) {
  const result = { ...torrent };
  for (const field of SENSITIVE_FIELDS) delete result[field];
  return result;
}

function extractTorrentId(comment) {
  const match = String(comment || "").match(/torrents\/(\d+)$/);
  return match ? Number(match[1]) : null;
}

export class QbittorrentClient {
  constructor(url) {
    this.url = url;
  }

  async request(path, { method = "GET", searchParams = null, body = null, expect = "json" } = {}) {
    const url = new URL(`${this.url}${path}`);
    if (searchParams) {
      for (const [key, value] of Object.entries(searchParams)) {
        if (value !== undefined && value !== null && value !== "") url.searchParams.set(key, String(value));
      }
    }
    const response = await fetch(url, { method, body });
    if (!response.ok) {
      const text = await response.text();
      throw new Error(`qBittorrent request failed: ${response.status} ${text}`);
    }
    return expect === "text" ? response.text() : response.json();
  }

  async allTorrents() {
    return this.request("/api/v2/torrents/info");
  }

  async findByUnitId(id) {
    const parsed = parseInt(id, 10);
    if (Number.isNaN(parsed)) return null;
    const torrents = await this.allTorrents();
    const match = torrents.find((t) => extractTorrentId(t.comment) === parsed);
    return match ? redact(match) : null;
  }

  async addTorrentByUrl(torrentUrl, savePath) {
    const formData = new FormData();
    formData.append("urls", torrentUrl);
    formData.append("savepath", savePath);

    await this.request("/api/v2/torrents/add", {
      method: "POST",
      body: formData,
      expect: "text"
    });
  }
}
