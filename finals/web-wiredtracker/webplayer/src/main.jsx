import React, { useEffect, useRef, useState } from "react";
import { createRoot } from "react-dom/client";

const styleText = `
@layer reset, base, atmosphere, components;

@layer reset {
  *, *::before, *::after { box-sizing: border-box; }
  html, body, #root { margin: 0; min-height: 100%; }
  button, input { font: inherit; color: inherit; }
  h1, h2, h3, p, ul, li { margin: 0; padding: 0; }
  ul, ol { list-style: none; }
}

@layer base {
  :root {
    color-scheme: dark;
    --ink: #d8d3b8;
    --ink-bright: #f4eed1;
    --ink-dim: #8a8268;
    --ink-faint: #4d4937;
    --olive: #9bac3f;
    --blood: #c01e1e;
    --blood-bright: #ef3434;
    --blood-glow: rgba(192, 30, 30, 0.45);
    --cyan: #5fd0e1;
    --bg-deep: #050507;
    --paper: #11111a;
    --paper-bright: #18181f;
    --hairline: rgba(216, 211, 184, 0.16);
    --hairline-strong: rgba(216, 211, 184, 0.4);
    --mono: "VT323", ui-monospace, "SF Mono", Menlo, Consolas, monospace;
    --display: "DotGothic16", "VT323", monospace;
  }

  html { background: var(--bg-deep); }

  body {
    font-family: var(--mono);
    font-size: 18px;
    line-height: 1.35;
    color: var(--ink);
    background:
      radial-gradient(ellipse 60% 40% at 80% -10%, rgba(192,30,30,0.16), transparent 60%),
      radial-gradient(ellipse 80% 60% at 10% 110%, rgba(155,172,63,0.06), transparent 60%),
      var(--bg-deep);
    min-height: 100vh;
    overflow-x: hidden;
    letter-spacing: 0.01em;
    animation: crt-flicker 7.5s steps(60, end) infinite;
  }

  ::selection { background: var(--blood); color: var(--ink-bright); }
  :focus-visible { outline: 1px solid var(--olive); outline-offset: 3px; }
}

@layer atmosphere {
  body::before {
    content: "";
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 1;
    background:
      repeating-linear-gradient(to bottom, transparent 0 2px, rgba(216,211,184,0.05) 2px 3px),
      url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='200' height='200'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='2' stitchTiles='stitch'/><feColorMatrix values='0 0 0 0 0.85  0 0 0 0 0.83  0 0 0 0 0.72  0 0 0 0.5 0'/></filter><rect width='100%25' height='100%25' filter='url(%23n)'/></svg>");
    background-size: auto, 200px 200px;
    mix-blend-mode: screen;
    opacity: 0.5;
    animation: noise 360ms steps(8, end) infinite;
  }

  body::after {
    content: "";
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 2;
    background: radial-gradient(ellipse at center, transparent 45%, rgba(0,0,0,0.7) 100%);
  }
}

@layer components {
  .shell {
    position: relative;
    z-index: 6;
    max-width: 760px;
    margin: 0 auto;
    padding: clamp(2rem, 5vw, 4.5rem) clamp(1.2rem, 3vw, 2rem) 12rem;
  }

  /* ─── Boot prompt ─── */
  .prompt {
    color: var(--ink-dim);
    font-size: 1rem;
    letter-spacing: 0.04em;
    margin-bottom: 1.4rem;
    display: flex;
    align-items: center;
    gap: 0.4em;
    flex-wrap: wrap;
  }
  .prompt b { color: var(--ink); font-weight: normal; }
  .prompt .arrow { color: var(--blood); }
  .prompt .caret {
    display: inline-block;
    width: 0.55ch;
    color: var(--ink);
    animation: blink 1.05s steps(2, end) infinite;
  }
  .prompt .stamp {
    margin-left: auto;
    font-family: var(--display);
    font-size: 0.72rem;
    letter-spacing: 0.32em;
    color: var(--blood);
    border: 1px solid var(--blood);
    padding: 0.15em 0.6em;
    text-transform: uppercase;
  }

  /* ─── Title ─── */
  .title-block { margin-bottom: 1.4rem; }
  .title {
    font-family: var(--display);
    font-size: clamp(3rem, 8.5vw, 5rem);
    line-height: 0.9;
    letter-spacing: -0.02em;
    color: var(--ink-bright);
    text-transform: lowercase;
    position: relative;
    text-shadow: 0 0 18px rgba(216,211,184,0.18);
    animation: glitch-shift 6.2s steps(40, end) infinite;
    display: inline-block;
  }
  .title-kanji {
    color: var(--blood);
    margin-right: 0.12em;
    text-shadow: 0 0 12px var(--blood-glow);
    font-family: var(--display);
  }
  .subtitle {
    margin-top: 0.5rem;
    font-family: var(--display);
    font-size: 0.82rem;
    color: var(--ink-dim);
    letter-spacing: 0.4em;
    text-transform: uppercase;
  }
  .subtitle em { font-style: normal; color: var(--blood); margin: 0 0.4em; }

  /* ─── Status ─── */
  .status {
    display: flex;
    align-items: center;
    gap: 0.8rem;
    padding: 0.7rem 1rem;
    margin: 2rem 0;
    background: var(--paper);
    border: 1px solid var(--hairline);
    font-size: 1rem;
    position: relative;
    overflow: hidden;
  }
  .status .led {
    width: 9px;
    height: 9px;
    background: var(--blood);
    box-shadow: 0 0 8px var(--blood), 0 0 18px var(--blood-glow);
    animation: pulse 1.6s ease-in-out infinite;
    flex-shrink: 0;
  }

  /* ─── Section headers ─── */
  .section-head {
    display: grid;
    grid-template-columns: auto auto 1fr;
    align-items: end;
    gap: 1rem;
    margin: 2.8rem 0 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--hairline);
  }
  .section-head .sh-num {
    font-family: var(--display);
    font-size: 2.4rem;
    color: var(--blood);
    line-height: 0.9;
    text-shadow: 0 0 12px var(--blood-glow);
  }
  .section-head .sh-en {
    font-family: var(--display);
    font-size: 1.3rem;
    letter-spacing: 0.28em;
    color: var(--ink-bright);
    text-transform: uppercase;
    padding-bottom: 0.2em;
  }
  .section-head .sh-line {
    height: 1px;
    background: linear-gradient(to right, var(--hairline-strong), transparent);
    align-self: end;
    margin-bottom: 0.5em;
  }

  /* ─── Transmission cards ─── */
  .torrents { display: flex; flex-direction: column; gap: 0.7rem; }
  .torrent {
    position: relative;
    display: grid;
    grid-template-columns: 1fr auto;
    gap: 1.2rem;
    align-items: center;
    padding: 1rem 1.2rem;
    background: var(--paper);
    border: 1px solid var(--hairline);
    transition: border-color 200ms, background 200ms;
  }
  .torrent::before, .torrent::after {
    content: "";
    position: absolute;
    width: 12px;
    height: 12px;
    border: 1px solid var(--blood);
    opacity: 0;
    transition: opacity 220ms;
  }
  .torrent::before { top: -1px; left: -1px; border-right: none; border-bottom: none; }
  .torrent::after { bottom: -1px; right: -1px; border-left: none; border-top: none; }
  .torrent:hover {
    border-color: var(--blood);
    background: var(--paper-bright);
  }
  .torrent:hover::before, .torrent:hover::after { opacity: 1; }

  .torrent-meta {
    display: grid;
    grid-template-columns: auto 1fr;
    gap: 0.2rem 0.8rem;
    align-items: baseline;
    min-width: 0;
  }
  .torrent-meta .t-title {
    grid-column: 1 / -1;
    color: var(--ink-bright);
    font-size: 1.15rem;
    line-height: 1.2;
    margin-bottom: 0.3em;
    word-break: break-word;
  }
  .torrent-meta .t-tag {
    font-family: var(--display);
    color: var(--blood);
    letter-spacing: 0.2em;
    font-size: 0.72rem;
  }
  .torrent-meta .t-val { color: var(--ink); font-size: 0.95rem; }

  .jack-btn {
    appearance: none;
    background: transparent;
    border: 1px solid var(--ink-dim);
    color: var(--ink);
    font-family: var(--display);
    font-size: 0.95rem;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    padding: 0.7rem 1.2rem;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 0.6rem;
    position: relative;
    overflow: hidden;
    transition: color 160ms, border-color 160ms, transform 100ms;
    z-index: 0;
  }
  .jack-btn .jack-icon { color: var(--blood); }
  .jack-btn::before {
    content: "";
    position: absolute;
    inset: 0;
    background: var(--blood);
    transform: translateX(-101%);
    transition: transform 240ms cubic-bezier(0.7, 0, 0.2, 1);
    z-index: -1;
  }
  .jack-btn:hover:not(:disabled) {
    color: var(--ink-bright);
    border-color: var(--blood);
  }
  .jack-btn:hover:not(:disabled)::before { transform: translateX(0); }
  .jack-btn:hover:not(:disabled) .jack-icon { color: var(--ink-bright); }
  .jack-btn:active:not(:disabled) { transform: translateY(1px); }
  .jack-btn:disabled { opacity: 0.4; cursor: not-allowed; }

  .empty {
    padding: 2.2rem 1rem;
    text-align: center;
    color: var(--ink-dim);
    border: 1px dashed var(--hairline);
    font-family: var(--display);
    letter-spacing: 0.15em;
  }
  .empty em { font-style: normal; color: var(--blood); }

  /* ─── Channels ─── */
  .channels {
    display: flex;
    flex-direction: column;
    gap: 2px;
    border: 1px solid var(--hairline);
    background: var(--paper);
  }
  .channel {
    display: grid;
    grid-template-columns: auto 1fr auto;
    gap: 1rem;
    align-items: center;
    padding: 0.6rem 0.95rem;
    border-left: 2px solid transparent;
    cursor: pointer;
    font-size: 1rem;
    transition: background 160ms, border-color 160ms;
  }
  .channel .ch-num {
    font-family: var(--display);
    color: var(--blood);
    font-size: 0.82rem;
    letter-spacing: 0.18em;
    min-width: 5ch;
  }
  .channel .ch-name {
    color: var(--ink-dim);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  .channel .ch-state {
    font-family: var(--display);
    color: var(--olive);
    font-size: 0.78rem;
    letter-spacing: 0.18em;
  }
  .channel:hover {
    background: rgba(192, 30, 30, 0.04);
    border-left-color: var(--olive);
  }
  .channel:hover .ch-name { color: var(--ink); }
  .channel.active {
    background: rgba(192, 30, 30, 0.09);
    border-left-color: var(--blood-bright);
  }
  .channel.active .ch-num { color: var(--blood-bright); }
  .channel.active .ch-name { color: var(--ink-bright); }

  /* ─── Dock ─── */
  .dock {
    position: fixed;
    left: clamp(0.6rem, 2vw, 1.4rem);
    right: clamp(0.6rem, 2vw, 1.4rem);
    bottom: clamp(0.6rem, 2vw, 1rem);
    z-index: 40;
    padding: 0.9rem 1.2rem 1rem;
    display: grid;
    grid-template-columns: minmax(0, 1.1fr) minmax(0, 1.8fr) minmax(170px, 0.7fr);
    gap: 1.4rem;
    align-items: center;
    background: linear-gradient(180deg, rgba(17,17,26,0.94), rgba(10,10,16,0.94));
    border: 1px solid var(--hairline-strong);
    backdrop-filter: blur(20px) saturate(140%);
    box-shadow:
      inset 0 0 0 1px rgba(192, 30, 30, 0.18),
      0 -10px 50px rgba(0,0,0,0.6);
  }
  .dock::before {
    content: "";
    position: absolute;
    top: -1px;
    left: 18px;
    width: 80px;
    height: 2px;
    background: var(--blood);
    box-shadow: 0 0 8px var(--blood-glow);
  }

  .dock-side { min-width: 0; }
  .dock-label {
    font-family: var(--display);
    font-size: 0.7rem;
    color: var(--blood);
    letter-spacing: 0.32em;
    text-transform: uppercase;
    margin-bottom: 0.35rem;
  }
  .dock-title {
    color: var(--ink-bright);
    font-size: 1.05rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  .dock-sub {
    color: var(--ink-dim);
    font-size: 0.88rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    margin-top: 0.1rem;
  }
  .dock-empty {
    color: var(--ink-dim);
    font-style: italic;
  }

  .dock-mid { display: grid; gap: 0.4rem; min-width: 0; }
  .controls {
    display: flex;
    gap: 0.4rem;
    justify-content: center;
    align-items: center;
  }
  .controls button {
    min-width: 40px;
    height: 40px;
    background: transparent;
    border: 1px solid var(--ink-dim);
    color: var(--ink);
    font-family: var(--mono);
    font-size: 1.05rem;
    cursor: pointer;
    transition: all 140ms;
    display: grid;
    place-items: center;
  }
  .controls button:hover:not(:disabled) {
    border-color: var(--blood);
    color: var(--blood-bright);
  }
  .controls button:disabled { opacity: 0.35; cursor: not-allowed; }
  .controls .play {
    min-width: 52px;
    height: 52px;
    border-color: var(--blood);
    color: var(--blood);
    box-shadow: 0 0 14px var(--blood-glow);
    font-size: 1.15rem;
  }
  .controls .play:hover:not(:disabled) {
    background: var(--blood);
    color: var(--ink-bright);
  }

  .time-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    color: var(--ink-dim);
    font-size: 0.9rem;
    letter-spacing: 0.08em;
    font-variant-numeric: tabular-nums;
  }
  .time-row .time-sep { color: var(--blood); }

  .vol-display {
    text-align: right;
    color: var(--ink-bright);
    font-size: 0.88rem;
    letter-spacing: 0.15em;
    margin-top: 0.2rem;
    font-variant-numeric: tabular-nums;
  }

  /* ─── Range sliders ─── */
  input[type="range"] {
    -webkit-appearance: none;
    appearance: none;
    width: 100%;
    height: 18px;
    background: transparent;
    cursor: pointer;
  }
  input[type="range"]::-webkit-slider-runnable-track {
    height: 2px;
    background: linear-gradient(
      to right,
      var(--blood) 0%,
      var(--blood) var(--progress, 0%),
      var(--ink-faint) var(--progress, 0%),
      var(--ink-faint) 100%
    );
    border: none;
  }
  input[type="range"]::-moz-range-track { height: 2px; background: var(--ink-faint); }
  input[type="range"]::-moz-range-progress { height: 2px; background: var(--blood); }
  input[type="range"]::-webkit-slider-thumb {
    -webkit-appearance: none;
    appearance: none;
    width: 12px;
    height: 16px;
    background: var(--ink-bright);
    border: none;
    margin-top: -7px;
    box-shadow: 0 0 8px var(--blood-glow);
    transition: background 120ms;
  }
  input[type="range"]::-moz-range-thumb {
    width: 12px;
    height: 16px;
    background: var(--ink-bright);
    border: none;
  }
  input[type="range"]:hover::-webkit-slider-thumb { background: var(--blood-bright); }

  @media (max-width: 720px) {
    .shell { padding-bottom: 16rem; }
    .dock {
      grid-template-columns: 1fr;
      gap: 0.6rem;
      padding: 0.85rem;
    }
    .dock-side.dock-vol { display: none; }
    .torrent { grid-template-columns: 1fr; }
    .jack-btn { justify-self: start; }
  }
}

/* ─── Animations ─── */
@keyframes blink {
  0%, 49% { opacity: 1; }
  50%, 100% { opacity: 0; }
}
@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.55; transform: scale(0.85); }
}
@keyframes sweep {
  0% { transform: translateX(-100%); }
  60%, 100% { transform: translateX(100%); }
}
@keyframes crt-flicker {
  0%, 92%, 100% { filter: none; }
  93% { filter: brightness(1.06); }
  95% { filter: brightness(0.9); }
}
@keyframes noise {
  0%   { background-position: 0 0, 0 0; }
  25%  { background-position: 0 0, -40px 20px; }
  50%  { background-position: 0 0, 30px -10px; }
  75%  { background-position: 0 0, -20px 40px; }
  100% { background-position: 0 0, 0 0; }
}
@keyframes glitch-r {
  0%, 100% { transform: translate(0, 0); clip-path: inset(0 0 0 0); }
  20% { transform: translate(-2px, 0); clip-path: inset(40% 0 30% 0); }
  40% { transform: translate(2px, 1px); clip-path: inset(70% 0 5% 0); }
  60%, 90% { transform: translate(0, 0); clip-path: inset(0 0 0 0); }
}
@keyframes glitch-b {
  0%, 100% { transform: translate(0, 0); clip-path: inset(0 0 0 0); }
  25% { transform: translate(2px, 0); clip-path: inset(50% 0 20% 0); }
  45% { transform: translate(-1px, -1px); clip-path: inset(20% 0 70% 0); }
  65%, 95% { transform: translate(0, 0); clip-path: inset(0 0 0 0); }
}
@keyframes glitch-shift {
  0%, 90%, 100% { transform: translate(0, 0); }
  92% { transform: translate(-1px, 1px); }
  94% { transform: translate(2px, -1px); }
  96% { transform: translate(-1px, 0); }
}

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0ms !important;
    transition-duration: 0ms !important;
  }
}
`;

if (!document.getElementById("webplayer-style")) {
  const s = document.createElement("style");
  s.id = "webplayer-style";
  s.textContent = styleText;
  document.head.appendChild(s);
}

async function api(path, options = {}) {
  const headers = new Headers(options.headers || {});
  if (options.body && !headers.has("Content-Type")) headers.set("Content-Type", "application/json");
  const res = await fetch(path, { ...options, headers });
  if (res.status === 204) return null;
  const data = await res.json().catch(() => ({}));
  if (!res.ok || data.success === false) throw new Error(data.error || `Request failed (${res.status})`);
  return data;
}

function formatTime(seconds) {
  if (!Number.isFinite(seconds)) return "0:00";
  const s = Math.floor(seconds);
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;
}

function formatSpeed(bps) {
  if (bps <= 0) return "";
  if (bps < 1024) return `${bps} B/s`;
  if (bps < 1024 * 1024) return `${(bps / 1024).toFixed(1)} KB/s`;
  return `${(bps / (1024 * 1024)).toFixed(1)} MB/s`;
}

const STATE_LABELS = {
  downloading: "Receiving", stalledDL: "Signal stalled", pausedDL: "Paused", queuedDL: "Queued",
  metaDL: "Negotiating Protocol 7", uploading: "Broadcasting", stalledUP: "Broadcasting (idle)",
  pausedUP: "Complete", error: "Transmission error", missingFiles: "Payload missing"
};

function SectionHead({ num, en }) {
  return (
    <div className="section-head">
      <span className="sh-num">{num}</span>
      <span className="sh-en">{en}</span>
      <span className="sh-line" aria-hidden="true" />
    </div>
  );
}

function App() {
  const [torrents, setTorrents] = useState([]);
  const [busyId, setBusyId] = useState(null);
  const [statusText, setStatusText] = useState("Connecting to the Wired...");
  const [queue, setQueue] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(-1);
  const [isPlaying, setIsPlaying] = useState(false);
  const [volume, setVolume] = useState(0.8);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const audioRef = useRef(null);
  const shouldAutoplayRef = useRef(false);

  const currentTrack = currentIndex >= 0 ? queue[currentIndex] || null : null;

  useEffect(() => {
    api("/api/torrents").then((data) => {
      setTorrents(data.torrents || []);
      setStatusText(data.torrents?.length ? "Link established. Protocol 7 active." : "The Wired is silent. No transmissions detected.");
    }).catch((e) => setStatusText(e.message));
  }, []);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio || !currentTrack) return;
    audio.src = `/api/stream-audio?path=${encodeURIComponent(currentTrack.path)}`;
    audio.load();
    if (shouldAutoplayRef.current) {
      audio.play().then(() => setIsPlaying(true)).catch(() => setIsPlaying(false));
      shouldAutoplayRef.current = false;
    } else {
      setIsPlaying(false);
    }
  }, [currentTrack?.id]);

  useEffect(() => { if (audioRef.current) audioRef.current.volume = volume; }, [volume]);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;
    const onTime = () => setCurrentTime(audio.currentTime);
    const onMeta = () => setDuration(audio.duration || 0);
    const onPlay = () => setIsPlaying(true);
    const onPause = () => setIsPlaying(false);
    const onEnd = () => {
      if (queue.length === 0) return;
      shouldAutoplayRef.current = true;
      setCurrentIndex((i) => (i >= queue.length - 1 ? 0 : i + 1));
    };
    audio.addEventListener("timeupdate", onTime);
    audio.addEventListener("loadedmetadata", onMeta);
    audio.addEventListener("play", onPlay);
    audio.addEventListener("pause", onPause);
    audio.addEventListener("ended", onEnd);
    return () => {
      audio.removeEventListener("timeupdate", onTime);
      audio.removeEventListener("loadedmetadata", onMeta);
      audio.removeEventListener("play", onPlay);
      audio.removeEventListener("pause", onPause);
      audio.removeEventListener("ended", onEnd);
    };
  }, [queue, currentIndex]);

  const handleListen = async (torrent) => {
    setBusyId(torrent.id);
    try {
      setStatusText("Requesting transmission...");
      await api("/api/request-torrent", { method: "POST", body: JSON.stringify({ id: torrent.id }) });

      for (let i = 0; i < 120; i++) {
        try {
          const data = await api(`/api/torrent-status/${torrent.id}`);
          const t = data.torrent || {};
          const progress = Number(t.progress || 0);
          if (progress >= 1) { setStatusText("Transmission received. Decoding payload..."); break; }
          const label = STATE_LABELS[t.state] || t.state || "Working";
          const speed = formatSpeed(t.dlspeed || 0);
          setStatusText(`${label} — ${Math.round(progress * 100)}%${speed ? ` @ ${speed}` : ""}`);
        } catch {
          setStatusText("Waiting for relay node...");
        }
        await new Promise((r) => setTimeout(r, 2000));
      }

      let files = [];
      for (let i = 0; i < 10; i++) {
        try {
          const data = await api(`/api/audio-files/${torrent.id}`);
          files = data.files || [];
          if (files.length > 0) break;
        } catch { /* retry */ }
        await new Promise((r) => setTimeout(r, 3000));
      }

      if (files.length === 0) { setStatusText("No audio payload in this transmission."); return; }

      const items = files.map((f, i) => ({ id: `${torrent.id}-${i}`, name: f.name, path: f.path, title: torrent.title }));
      setQueue(items);
      shouldAutoplayRef.current = true;
      setCurrentIndex(0);
      setStatusText("Signal acquired. Channel locked.");
    } catch (error) {
      setStatusText(error.message);
    } finally {
      setBusyId(null);
    }
  };

  const togglePlay = async () => {
    const audio = audioRef.current;
    if (!audio || !currentTrack) return;
    if (audio.paused) { try { await audio.play(); } catch (e) { setStatusText(e.message); } }
    else audio.pause();
  };

  const prev = () => { if (queue.length) { shouldAutoplayRef.current = true; setCurrentIndex((i) => (i <= 0 ? queue.length - 1 : i - 1)); } };
  const next = () => { if (queue.length) { shouldAutoplayRef.current = true; setCurrentIndex((i) => (i >= queue.length - 1 ? 0 : i + 1)); } };
  const seek = (v) => { if (audioRef.current) { audioRef.current.currentTime = v; setCurrentTime(v); } };

  const seekMax = Math.max(duration || 0, 1);
  const seekVal = Math.min(currentTime, duration || 0);
  const seekPct = duration > 0 ? (seekVal / seekMax) * 100 : 0;
  const volPct = volume * 100;

  return (
    <>
      <audio ref={audioRef} preload="metadata" />

      <main className="shell">
        <div className="prompt">
          <b>~/wired</b>
          <span className="arrow">$</span>
          <span>./navi</span>
          <span className="caret">█</span>
          <span className="stamp">Layer 07</span>
        </div>

        <div className="title-block">
          <h1 className="title" data-text="navi">
            <span className="title-kanji">接</span>navi
          </h1>
          <div className="subtitle">
            // THE WIRED <em>—</em> PRESENT DAY. PRESENT TIME.
          </div>
        </div>

        <div className="status" role="status">
          <span className="led" aria-hidden="true" />
          <span>{statusText}</span>
        </div>

        <SectionHead num="01" en="TRANSMISSIONS" />

        <ul className="torrents">
          {torrents.map((t) => (
            <li key={t.id} className="torrent">
              <div className="torrent-meta">
                <h2 className="t-title">{t.title}</h2>
                {t.size && <>
                  <span className="t-tag">SIZE</span>
                  <span className="t-val">{t.size}</span>
                </>}
                <span className="t-tag">RELAYS</span>
                <span className="t-val">{t.seeders}</span>
              </div>
              <button className="jack-btn" disabled={busyId === t.id} onClick={() => handleListen(t)}>
                <span className="jack-icon">◉</span>
                <span>{busyId === t.id ? "Patching…" : "Jack in"}</span>
              </button>
            </li>
          ))}
          {torrents.length === 0 && (
            <li className="empty">// the wired is silent <em>//</em> stand by for transmission</li>
          )}
        </ul>

        {queue.length > 0 && (
          <>
            <SectionHead num="02" en="CHANNELS" />
            <ul className="channels">
              {queue.map((track, i) => (
                <li
                  key={track.id}
                  className={`channel${i === currentIndex ? " active" : ""}`}
                  onClick={() => { shouldAutoplayRef.current = true; setCurrentIndex(i); }}
                >
                  <span className="ch-num">CH{String(i + 1).padStart(2, "0")}</span>
                  <span className="ch-name">{track.name}</span>
                  <span className="ch-state">
                    {i === currentIndex ? (isPlaying ? "● BROADCAST" : "○ HOLD") : ""}
                  </span>
                </li>
              ))}
            </ul>
          </>
        )}
      </main>

      <footer className="dock">
        <div className="dock-side">
          <div className="dock-label">Now Broadcasting</div>
          {currentTrack ? (
            <>
              <div className="dock-title">{currentTrack.name}</div>
              <div className="dock-sub">{currentTrack.title}</div>
            </>
          ) : (
            <div className="dock-empty">// no signal acquired //</div>
          )}
        </div>

        <div className="dock-mid">
          <div className="controls">
            <button onClick={prev} disabled={queue.length === 0} aria-label="Previous">⏮</button>
            <button className="play" onClick={togglePlay} disabled={queue.length === 0} aria-label={isPlaying ? "Pause" : "Play"}>
              {isPlaying ? "▮▮" : "▶"}
            </button>
            <button onClick={next} disabled={queue.length === 0} aria-label="Next">⏭</button>
          </div>
          <input
            type="range"
            min="0"
            max={seekMax}
            value={seekVal}
            onChange={(e) => seek(Number(e.target.value))}
            style={{ "--progress": `${seekPct}%` }}
            aria-label="Seek"
          />
          <div className="time-row">
            <span>{formatTime(currentTime)}</span>
            <span className="time-sep">::</span>
            <span>{formatTime(duration)}</span>
          </div>
        </div>

        <div className="dock-side dock-vol">
          <div className="dock-label">Gain</div>
          <input
            type="range"
            min="0"
            max="1"
            step="0.01"
            value={volume}
            onChange={(e) => setVolume(Number(e.target.value))}
            style={{ "--progress": `${volPct}%` }}
            aria-label="Volume"
          />
          <div className="vol-display">{String(Math.round(volume * 100)).padStart(3, "0")}%</div>
        </div>
      </footer>
    </>
  );
}

createRoot(document.getElementById("root")).render(<App />);
