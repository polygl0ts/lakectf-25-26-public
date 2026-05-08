import fs from "node:fs";
import fsp from "node:fs/promises";
import path from "node:path";
import http from "node:http";
import express from "express";

import { config } from "./config.mjs";
import { listTorrentsFromRss } from "./db.mjs";
import { QbittorrentClient } from "./qbittorrent.mjs";
import { ensureSafePath, getMimeType, parseRange, rangeHeaders, walkAudioFiles } from "./utils.mjs";

await fsp.mkdir(config.downloadsDir, { recursive: true });

const qb = new QbittorrentClient(config.qbittorrentUrl);

function torrentDownloadUrl(id) {
  return `${config.trackerBaseUrl}/torrent/download/${parseInt(id, 10)}.${config.trackerRssKey}`;
}

async function locateTorrentOnDisk(id) {
  const t = await qb.findByUnitId(id);
  if (!t) return null;
  const candidates = [t.content_path, t.save_path ? path.join(t.save_path, t.name) : null, t.save_path].filter(Boolean);
  for (const c of candidates) {
    try {
      const stat = await fsp.stat(c);
      return stat.isDirectory() ? c : path.dirname(c);
    } catch { continue; }
  }
  return null;
}

const app = express();
app.use(express.json());

// List torrents from the RSS feed.
app.get("/api/torrents", async (req, res) => {
  try {
    const torrents = await listTorrentsFromRss(config.trackerBaseUrl, config.trackerRssFeedId, config.trackerRssKey);
    res.json({ success: true, torrents });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Request a torrent by UNIT3D id — add to qBittorrent if not already there.
app.post("/api/request-torrent", async (req, res) => {
  try {
    const { id } = req.body;
    if (!id) return res.status(400).json({ success: false, error: "Missing id." });

    let t = await qb.findByUnitId(id);
    if (!t) {
      await qb.addTorrentByUrl(torrentDownloadUrl(id), config.downloadsDir);
    }

    res.json({ success: true });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Poll torrent status by UNIT3D id.
app.get("/api/torrent-status/:id", async (req, res) => {
  try {
    const t = await qb.findByUnitId(req.params.id);
    if (!t) return res.status(404).json({ success: false, error: "Not found in qBittorrent." });
    res.json({ success: true, torrent: t });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Find audio files for a completed torrent by UNIT3D id.
app.get("/api/audio-files/:id", async (req, res) => {
  try {
    const dir = await locateTorrentOnDisk(req.params.id);
    if (!dir) return res.status(404).json({ success: false, error: "Torrent path not available yet." });
    const files = await walkAudioFiles(dir);
    if (files.length === 0) return res.status(404).json({ success: false, error: "No audio files yet." });
    res.json({ success: true, files });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Stream an audio file.
app.get("/api/stream-audio", async (req, res) => {
  try {
    const requestedPath = decodeURIComponent(req.query.path || "");
    if (!requestedPath) return res.status(400).json({ success: false, error: "Missing path." });

    const safePath = ensureSafePath(config.downloadsDir, requestedPath);
    const stat = await fsp.stat(safePath);
    const range = parseRange(req.headers.range, stat.size);
    const mime = getMimeType(safePath);

    if (!range) {
      res.writeHead(200, { "Content-Type": mime, "Content-Length": stat.size, "Accept-Ranges": "bytes", "Cache-Control": "no-store" });
      fs.createReadStream(safePath).pipe(res);
      return;
    }
    res.writeHead(206, { "Content-Type": mime, "Cache-Control": "no-store", ...rangeHeaders(range.start, range.end, stat.size) });
    fs.createReadStream(safePath, { start: range.start, end: range.end }).pipe(res);
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

app.use(express.static(config.distDir));
app.use((req, res) => res.sendFile(path.join(config.distDir, "index.html")));

http.createServer(app).listen(config.port, () => {
  console.log(`Webplayer listening on ${config.port}`);
});
