import fs from "node:fs/promises";
import path from "node:path";

const AUDIO_EXTENSIONS = new Set([".aac", ".aiff", ".alac", ".ape", ".flac", ".m4a", ".mp3", ".ogg", ".opus", ".wav", ".wma"]);

const MIME_TYPES = {
  ".m4a": "audio/mp4",
  ".mp3": "audio/mpeg",
  ".ogg": "audio/ogg",
  ".opus": "audio/ogg",
  ".wav": "audio/wav",
  ".flac": "audio/flac"
};

export function getMimeType(filePath) {
  return MIME_TYPES[path.extname(filePath).toLowerCase()] || "application/octet-stream";
}

export function ensureSafePath(rootDir, requestedPath) {
  const resolvedRoot = path.resolve(rootDir);
  const resolvedTarget = path.resolve(requestedPath);
  const rootWithSep = resolvedRoot.endsWith(path.sep) ? resolvedRoot : `${resolvedRoot}${path.sep}`;
  if (resolvedTarget !== resolvedRoot && !resolvedTarget.startsWith(rootWithSep)) {
    throw new Error("Requested path is outside the allowed root.");
  }
  return resolvedTarget;
}

export function rangeHeaders(start, end, size) {
  return {
    "Accept-Ranges": "bytes",
    "Content-Range": `bytes ${start}-${end}/${size}`,
    "Content-Length": end - start + 1
  };
}

export function parseRange(rangeHeader, size) {
  if (!rangeHeader?.startsWith("bytes=")) return null;
  const [startText, endText] = rangeHeader.slice("bytes=".length).split("-", 2);
  const start = startText === "" ? NaN : Number(startText);
  const end = endText === "" ? NaN : Number(endText);
  if (Number.isNaN(start) && Number.isNaN(end)) return null;
  if (Number.isNaN(start)) {
    const tail = Math.min(end, size);
    return { start: Math.max(0, size - tail), end: size - 1 };
  }
  return { start, end: Number.isNaN(end) ? size - 1 : Math.min(end, size - 1) };
}

export async function walkAudioFiles(rootPath) {
  const entries = await fs.readdir(rootPath, { withFileTypes: true });
  const files = [];
  for (const entry of entries) {
    const fullPath = path.join(rootPath, entry.name);
    if (entry.isDirectory()) {
      files.push(...(await walkAudioFiles(fullPath)));
      continue;
    }
    if (AUDIO_EXTENSIONS.has(path.extname(entry.name).toLowerCase())) {
      const stat = await fs.stat(fullPath);
      files.push({ name: entry.name, path: fullPath, size: stat.size });
    }
  }
  files.sort((a, b) => a.path.localeCompare(b.path, undefined, { numeric: true }));
  return files;
}
