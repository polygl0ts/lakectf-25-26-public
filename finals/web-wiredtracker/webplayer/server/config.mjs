import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export const config = {
  port: 3000,
  distDir: path.resolve(__dirname, "../dist"),
  downloadsDir: "/downloads",
  trackerBaseUrl: (process.env.APP_URL || "http://unit3d").replace(/\/$/, ""),
  trackerRssFeedId: Number(process.env.TRACKER_RSS_FEED_ID || 1),
  trackerRssKey: process.env.BOT_RSS_KEY,
  qbittorrentUrl: "http://127.0.0.1:8080"
};
