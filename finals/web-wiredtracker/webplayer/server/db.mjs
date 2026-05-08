const ITEM_REGEX = /<item>([\s\S]*?)<\/item>/gi;

function decodeXml(value) {
  return String(value || "")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"')
    .replace(/&#039;/g, "'")
    .replace(/&amp;/g, "&");
}

function getTagValue(block, tagName) {
  const match = block.match(new RegExp(`<${tagName}>([\\s\\S]*?)<\\/${tagName}>`, "i"));
  return match ? decodeXml(match[1].trim()) : "";
}

function stripHtml(value) {
  return decodeXml(String(value || "").replace(/<[^>]+>/g, " ")).replace(/\s+/g, " ").trim();
}

function readField(text, label) {
  const escaped = label.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const match = text.match(new RegExp(`<strong>${escaped}<\\/strong>:\\s*([\\s\\S]*?)(?:<br>|<\\/p>)`, "i"));
  return stripHtml(match ? match[1] : "");
}

export async function listTorrentsFromRss(trackerBaseUrl, rssFeedId, rssKey) {
  const feedUrl = `${trackerBaseUrl}/rss/${rssFeedId}.${rssKey}`;
  const response = await fetch(feedUrl);
  if (!response.ok) throw new Error(`RSS request failed: ${response.status}`);
  const xml = await response.text();

  const items = [];
  for (const match of xml.matchAll(ITEM_REGEX)) {
    const block = match[1];
    const title = getTagValue(block, "title");
    const link = getTagValue(block, "link");
    const desc = getTagValue(block, "description");
    const idMatch = link.match(/\/torrent\/download\/(\d+)\./i);
    const id = idMatch ? Number(idMatch[1]) : Number(getTagValue(block, "guid"));

    items.push({
      id,
      title,
      size: readField(desc, "Size") || "",
      seeders: Number.parseInt(readField(desc, "Seeders"), 10) || 0,
    });
  }
  return items;
}
