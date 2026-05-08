#!/usr/bin/env python3
"""
Simple bomb-defuse style GUI: enter a 4-digit code.
Change CORRECT_CODE and FLAG at the top for your challenge.
"""

import argparse
import random
import tkinter as tk
from tkinter import font as tkfont
from typing import Any, Optional


# --- Challenge configuration (edit these) ---
CORRECT_CODE = "1234"  # four digits, e.g. "1337"
FLAG = "EFPL{M0DUL471NG_S1gn4ls_C4n_b3_RF_Sn1ff3d}"

# Colors
COLOR_SUCCESS_BG = "#0d4d2d"
COLOR_SUCCESS_FG = "#c8ffd4"
COLOR_FAIL_BG = "#4a0a0a"
COLOR_FAIL_FG = "#ffcccc"
COLOR_FAIL_ACCENT = "#ff6600"


class BombDefuseApp:
    def __init__(self, start_fullscreen: bool = False) -> None:
        self.root = tk.Tk()
        self.root.title("Defuse")
        self.root.minsize(480, 320)
        self.root.configure(bg="#1a1a2e")

        self._fullscreen = bool(start_fullscreen)
        if self._fullscreen:
            self.root.attributes("-fullscreen", True)
        self._explosion_after_id: Optional[int] = None
        self._particles: list[dict[str, Any]] = []

        self.root.bind("<F11>", self._toggle_fullscreen)
        self.root.bind("<Escape>", self._on_escape)

        self._build_entry_screen()

    def _toggle_fullscreen(self, _event: Optional[tk.Event] = None) -> Optional[str]:
        self._fullscreen = not self._fullscreen
        self.root.attributes("-fullscreen", self._fullscreen)
        return "break"

    def _on_escape(self, _event: Optional[tk.Event] = None) -> Optional[str]:
        if self._fullscreen:
            self._fullscreen = False
            self.root.attributes("-fullscreen", False)
        return "break"

    def _clear_root(self) -> None:
        if self._explosion_after_id is not None:
            self.root.after_cancel(self._explosion_after_id)
            self._explosion_after_id = None
        self._particles.clear()
        for w in self.root.winfo_children():
            w.destroy()

    def _build_entry_screen(self) -> None:
        self._clear_root()

        outer = tk.Frame(self.root, bg="#1a1a2e")
        outer.pack(fill=tk.BOTH, expand=True)

        hint = tk.Label(
            outer,
            text="Enter 4-digit disarm code",
            font=("Segoe UI", 14),
            fg="#eaeaea",
            bg="#1a1a2e",
        )
        hint.pack(pady=(40, 12))

        self.code_var = tk.StringVar()
        entry = tk.Entry(
            outer,
            textvariable=self.code_var,
            font=("Consolas", 28),
            width=6,
            justify=tk.CENTER,
            validate="key",
        )

        def only_digits(p: str) -> bool:
            return p == "" or (p.isdigit() and len(p) <= 4)

        entry.configure(validatecommand=(self.root.register(only_digits), "%P"))
        entry.pack(pady=8)
        entry.focus_set()
        entry.bind("<Return>", lambda e: self._try_defuse())

        btn_frame = tk.Frame(outer, bg="#1a1a2e")
        btn_frame.pack(pady=16)

        tk.Button(
            btn_frame,
            text="Defuse",
            font=("Segoe UI", 12, "bold"),
            command=self._try_defuse,
            padx=24,
            pady=8,
        ).pack(side=tk.LEFT, padx=6)

        tk.Button(
            btn_frame,
            text="Fullscreen (F11)",
            font=("Segoe UI", 11),
            command=lambda: self._toggle_fullscreen(),
            padx=16,
            pady=8,
        ).pack(side=tk.LEFT, padx=6)

    def _try_defuse(self) -> None:
        code = self.code_var.get().strip()
        if len(code) != 4 or not code.isdigit():
            self.code_var.set("")
            return
        if code == CORRECT_CODE:
            self._show_success()
        else:
            self._show_explosion()

    def _show_success(self) -> None:
        self._clear_root()
        frame = tk.Frame(self.root, bg=COLOR_SUCCESS_BG)
        frame.pack(fill=tk.BOTH, expand=True)

        title_font = tkfont.Font(family="Segoe UI", size=36, weight="bold")
        flag_font = tkfont.Font(family="Consolas", size=18)

        tk.Label(
            frame,
            text="BOMB DEFUSED",
            font=title_font,
            fg=COLOR_SUCCESS_FG,
            bg=COLOR_SUCCESS_BG,
        ).pack(expand=True)

        tk.Label(
            frame,
            text=FLAG,
            font=flag_font,
            fg="#7fff9a",
            bg=COLOR_SUCCESS_BG,
            wraplength=self.root.winfo_screenwidth() - 80,
        ).pack(pady=(0, 60))

        tk.Button(
            frame,
            text="Back",
            command=self._build_entry_screen,
            font=("Segoe UI", 11),
        ).pack(pady=12)

    def _show_explosion(self) -> None:
        self._clear_root()
        frame = tk.Frame(self.root, bg=COLOR_FAIL_BG)
        frame.pack(fill=tk.BOTH, expand=True)

        self._fail_canvas = tk.Canvas(
            frame,
            bg=COLOR_FAIL_BG,
            highlightthickness=0,
            borderwidth=0,
        )
        self._fail_canvas.pack(fill=tk.BOTH, expand=True)

        msg_font = tkfont.Font(family="Segoe UI", size=32, weight="bold")
        self._fail_canvas.create_text(
            0,
            0,
            text="BOMB EXPLODED",
            fill=COLOR_FAIL_FG,
            font=msg_font,
            tags="msg",
        )

        sub_font = tkfont.Font(family="Segoe UI", size=14)
        self._fail_canvas.create_text(
            0,
            0,
            text="Wrong code",
            fill="#ff8888",
            font=sub_font,
            tags="sub",
        )

        tk.Button(
            frame,
            text="Try again",
            command=self._build_entry_screen,
            font=("Segoe UI", 11),
        ).pack(side=tk.BOTTOM, pady=12)

        self.root.update_idletasks()
        self._center_fail_text()
        self.root.bind("<Configure>", self._on_fail_configure)

        self._spawn_burst()
        self._explosion_tick()

    def _on_fail_configure(self, _event: tk.Event) -> None:
        self._center_fail_text()

    def _center_fail_text(self) -> None:
        w = self._fail_canvas.winfo_width()
        h = self._fail_canvas.winfo_height()
        if w < 2 or h < 2:
            return
        self._fail_canvas.coords("msg", w // 2, h // 2 - 28)
        self._fail_canvas.coords("sub", w // 2, h // 2 + 24)

    def _spawn_burst(self) -> None:
        w = max(self._fail_canvas.winfo_width(), 400)
        h = max(self._fail_canvas.winfo_height(), 300)
        cx, cy = w // 2, h // 2
        for _ in range(48):
            ang = random.uniform(0, 6.28318)
            spd = random.uniform(2.0, 9.0)
            r = random.uniform(4, 14)
            life = random.randint(25, 55)
            hue = random.choice(
                ["#ff2200", "#ff6600", "#ffaa00", "#ffff66", "#ff4444"]
            )
            self._particles.append(
                {
                    "x": cx + random.uniform(-20, 20),
                    "y": cy + random.uniform(-20, 20),
                    "vx": spd * random.uniform(0.7, 1.3) * (1 if random.random() > 0.5 else -1) * 0.5
                    + random.uniform(-1, 1),
                    "vy": spd * random.uniform(0.7, 1.3) * (1 if random.random() > 0.5 else -1) * 0.5
                    + random.uniform(-1, 1),
                    "r": r,
                    "life": life,
                    "max_life": life,
                    "fill": hue,
                    "id": None,
                }
            )

    def _explosion_tick(self) -> None:
        for p in self._particles:
            if p["id"] is None:
                p["id"] = self._fail_canvas.create_oval(
                    0, 0, 0, 0, fill=p["fill"], outline=""
                )
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["vy"] += 0.12
            p["life"] -= 1
            alpha = max(0, p["life"] / p["max_life"])
            rr = p["r"] * (0.5 + 0.5 * alpha)
            x0, y0 = p["x"] - rr, p["y"] - rr
            x1, y1 = p["x"] + rr, p["y"] + rr
            self._fail_canvas.coords(p["id"], x0, y0, x1, y1)
            if p["life"] <= 0:
                self._fail_canvas.delete(p["id"])
                p["id"] = "dead"

        self._particles = [p for p in self._particles if p["id"] != "dead"]

        if len(self._particles) < 30:
            self._spawn_burst()

        flash = random.randint(0, 5) == 0
        bg = "#2a0505" if flash else COLOR_FAIL_BG
        self._fail_canvas.configure(bg=bg)
        self.root.configure(bg=bg)

        self._explosion_after_id = self.root.after(35, self._explosion_tick)

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    parser = argparse.ArgumentParser(description="Bomb defuse demo GUI")
    parser.add_argument(
        "--fullscreen",
        "-f",
        action="store_true",
        help="Start in fullscreen (Escape to exit fullscreen)",
    )
    args = parser.parse_args()
    BombDefuseApp(start_fullscreen=args.fullscreen).run()


if __name__ == "__main__":
    main()
