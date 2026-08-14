#!/usr/bin/env python3
"""Generate animated dark/light project panels for the GitHub profile."""
from __future__ import annotations

import base64
import html
import json
import math
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "projects" / "merged.json"
DEFAULT_OUTPUT = ROOT / "projects"
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"
W = 1180
CARD_W = 578
CARD_H = 168
GAP = 14
MARGIN = 5

THEMES = {
    "dark": {
        "BG": "#0A101F", "PANEL": "#0C1426", "PANEL_BAR": "#0B1222",
        "CYAN": "#22D3EE", "VIOLET": "#A78BFA", "VIOLET2": "#7C3AED",
        "EMERALD": "#10B981", "TEXT": "#F8FAFC", "MUTED": "#94A3B8", "DIM": "#475569",
        "STROKE": "rgba(34,211,238,0.28)", "STROKE_HI": "rgba(34,211,238,0.5)",
        "STROKE_LO": "rgba(34,211,238,0.22)", "BARLINE": "rgba(255,255,255,0.08)",
        "RING_BG": "rgba(148,163,184,0.15)", "PILL_BG": "rgba(124,58,237,0.28)",
        "PILL_STROKE": "rgba(167,139,250,0.5)", "MONO_TX": "#EDE9FE",
    },
    "light": {
        "BG": "#F8FAFC", "PANEL": "#FFFFFF", "PANEL_BAR": "#F1F5F9",
        "CYAN": "#0891B2", "VIOLET": "#7C3AED", "VIOLET2": "#6D28D9",
        "EMERALD": "#059669", "TEXT": "#0F172A", "MUTED": "#475569", "DIM": "#94A3B8",
        "STROKE": "rgba(8,145,178,0.30)", "STROKE_HI": "rgba(8,145,178,0.55)",
        "STROKE_LO": "rgba(8,145,178,0.20)", "BARLINE": "rgba(0,0,0,0.08)",
        "RING_BG": "rgba(100,116,139,0.20)", "PILL_BG": "rgba(124,58,237,0.12)",
        "PILL_STROKE": "rgba(124,58,237,0.4)", "MONO_TX": "#FFFFFF",
    },
}

DONUT_COLORS = {
    "dark": ["#A78BFA", "#22D3EE", "#10B981", "#6366F1", "#64748B", "#94A3B8"],
    "light": ["#7C3AED", "#0891B2", "#059669", "#6366F1", "#64748B", "#94A3B8"],
}


def esc(value) -> str:
    return html.escape(str(value), quote=True)


def relative_time(iso: str | None) -> str:
    if not iso:
        return "n/a"
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        delta = datetime.now(timezone.utc) - dt
        if delta.days > 365:
            return f"{delta.days // 365}y ago"
        if delta.days > 30:
            return f"{delta.days // 30}mo ago"
        if delta.days > 0:
            return f"{delta.days}d ago"
        hours = delta.seconds // 3600
        return f"{hours}h ago" if hours else "just now"
    except ValueError:
        return "n/a"


def load_logo(path: str | None) -> str | None:
    if not path:
        return None
    candidates = [ROOT / "projects" / "logos" / path, ROOT / "logos" / path, ROOT / path]
    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            ext = candidate.suffix.lower()
            mime = {".png": "image/png", ".svg": "image/svg+xml", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}.get(ext)
            if mime:
                encoded = base64.b64encode(candidate.read_bytes()).decode("ascii")
                return f"data:{mime};base64,{encoded}"
    return None


def wrap_text(text: str, max_chars: int = 52, max_lines: int = 2):
    words = text.split()
    lines, current = [], ""
    for word in words:
        if len(current) + len(word) + 1 <= max_chars:
            current = (current + " " + word).strip()
        else:
            lines.append(current)
            current = word
            if len(lines) == max_lines:
                break
    if current and len(lines) < max_lines:
        lines.append(current)
    if len(lines) == max_lines and len(words) > sum(len(x.split()) for x in lines):
        lines[-1] = lines[-1][:max_chars - 3].rstrip() + "..."
    return lines


def donut_segments(languages: dict, cx: float, cy: float, r: float, begin: float, colors):
    total = sum(languages.values()) or 1
    entries = sorted(languages.items(), key=lambda item: -item[1])[:4]
    other = total - sum(value for _, value in entries)
    if other > 0:
        entries.append(("Other", other))

    circumference = 2 * math.pi * r
    offset = 0.0
    time = begin
    circles = []
    legend = []
    for index, (language, value) in enumerate(entries):
        fraction = value / total
        segment = fraction * circumference
        color = colors[index % len(colors)]
        circles.append(
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{color}" stroke-width="9" '
            f'stroke-dasharray="0 {circumference:.2f}" stroke-dashoffset="{-offset:.2f}" transform="rotate(-90 {cx} {cy})" opacity="1">'
            f'<animate attributeName="stroke-dasharray" from="0 {circumference:.2f}" to="{segment:.2f} {circumference-segment:.2f}" dur="0.6s" begin="{time:.2f}s" fill="freeze"/>'
            '</circle>'
        )
        legend.append((language, fraction, color))
        offset += segment
        time += 0.18
    return "".join(circles), legend


def card(project: dict, x: int, y: int, index: int, theme: dict, colors) -> str:
    begin = 0.25 + index * 0.15
    repo = str(project.get("repo", "")).strip().replace("https://github.com/", "").replace("http://github.com/", "").rstrip("/")
    href = f"https://github.com/{esc(repo)}"
    e = [f'<a href="{href}" target="_blank"><g opacity="1" transform="translate({x},{y})">']
    e.append(
        f'<rect width="{CARD_W}" height="{CARD_H}" rx="12" fill="{theme["PANEL"]}" stroke="{theme["STROKE"]}">'
        f'<animate attributeName="stroke" values="{theme["STROKE_LO"]};{theme["STROKE_HI"]};{theme["STROKE_LO"]}" dur="4.5s" begin="{begin+index*0.7:.2f}s" repeatCount="indefinite"/></rect>'
    )
    e += [f'<rect width="{CARD_W}" height="30" rx="12" fill="{theme["PANEL_BAR"]}"/>',
          f'<rect y="18" width="{CARD_W}" height="12" fill="{theme["PANEL_BAR"]}"/>',
          f'<line x1="0" y1="30" x2="{CARD_W}" y2="30" stroke="{theme["BARLINE"]}"/>',
          f'<text x="16" y="19" font-size="10" fill="{theme["MUTED"]}"><tspan fill="{theme["CYAN"]}">●</tspan> {esc(repo or "unconfigured")}</text>']

    active = False
    try:
        dt = datetime.fromisoformat(str(project.get("pushed_at", "")).replace("Z", "+00:00"))
        active = (datetime.now(timezone.utc) - dt).days <= 14
    except ValueError:
        pass
    if active:
        e.append(f'<circle cx="{CARD_W-16}" cy="15" r="3.5" fill="{theme["EMERALD"]}"><animate attributeName="opacity" values="1;0.25;1" dur="1.8s" repeatCount="indefinite"/></circle>')
    else:
        e.append(f'<circle cx="{CARD_W-16}" cy="15" r="3.5" fill="{theme["DIM"]}"/>')

    logo = load_logo(project.get("logo"))
    float_anim = f'<animateTransform attributeName="transform" type="translate" values="0 0;0 -2.5;0 0" dur="5s" begin="{begin+index*0.5:.2f}s" repeatCount="indefinite"/>'
    if logo:
        e.append(f'<g>{float_anim}<image x="16" y="44" width="40" height="40" href="{logo}" preserveAspectRatio="xMidYMid meet"/></g>')
    else:
        initial = esc((project.get("name") or "?")[0].upper())
        e.append(f'<g>{float_anim}<rect x="16" y="44" width="40" height="40" rx="9" fill="{theme["VIOLET2"]}" opacity="0.9"/><text x="36" y="71" text-anchor="middle" font-size="20" font-weight="700" fill="{theme["MONO_TX"]}">{initial}</text></g>')

    name = esc(project.get("name", "unnamed"))
    e.append(f'<text x="68" y="61" font-size="17" font-weight="700" fill="{theme["TEXT"]}">{name}<tspan fill="{theme["CYAN"]}">_<animate attributeName="opacity" values="1;0;1" dur="1.2s" begin="{begin+0.4:.2f}s" repeatCount="indefinite"/></tspan></text>')
    for line_index, line in enumerate(wrap_text(project.get("description", ""))):
        e.append(f'<text x="68" y="{80 + line_index*16}" font-size="11" fill="{theme["MUTED"]}">{esc(line)}</text>')

    tx = 68
    for tag in (project.get("tags") or [])[:3]:
        width = len(str(tag)) * 6.6 + 14
        e.append(f'<rect x="{tx:.0f}" y="118" width="{width:.0f}" height="17" rx="8.5" fill="{theme["PILL_BG"]}" stroke="{theme["PILL_STROKE"]}"/>')
        e.append(f'<text x="{tx+width/2:.0f}" y="130" text-anchor="middle" font-size="9.5" fill="{theme["VIOLET"]}">{esc(tag)}</text>')
        tx += width + 7

    e.append(f'<text x="68" y="155" font-size="11" fill="{theme["MUTED"]}"><tspan fill="{theme["CYAN"]}">★</tspan> {int(project.get("stars", 0) or 0)}<tspan fill="{theme["DIM"]}" dx="14">updated {relative_time(project.get("pushed_at"))}</tspan></text>')

    languages = project.get("languages") or {}
    if languages:
        cx, cy, r = CARD_W - 58, CARD_H // 2 + 6, 27
        segments, legend = donut_segments(languages, cx, cy, r, begin + 0.3, colors)
        e.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{theme["RING_BG"]}" stroke-width="9"/>')
        e.append(segments)
        e.append(f'<text x="{cx}" y="{cy+4}" text-anchor="middle" font-size="11" font-weight="700" fill="{theme["TEXT"]}">{legend[0][1]*100:.0f}%</text>')
        dot_x = cx - r - 92
        text_x = dot_x + 9
        ly = cy - 22
        for language, fraction, color in legend[:3]:
            e.append(f'<circle cx="{dot_x}" cy="{ly}" r="3.5" fill="{color}"/><text x="{text_x}" y="{ly+4}" font-size="10" fill="{theme["MUTED"]}">{esc(language)} {fraction*100:.0f}%</text>')
            ly += 18

    e += ['</g></a>']
    return "".join(e)


def build(projects: list[dict], theme_name: str) -> str:
    theme = THEMES[theme_name]
    rows = math.ceil(len(projects) / 2) if projects else 1
    height = 56 + rows * (CARD_H + GAP) + MARGIN
    gid = f"acc-{theme_name}"
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{height}" viewBox="0 0 {W} {height}" font-family="{FONT}" role="img" aria-label="Ashish Raj projects">',
        f'<rect width="{W}" height="{height}" fill="{theme["BG"]}"/>',
        f'<defs><linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="{theme["VIOLET2"]}"><animate attributeName="stop-color" values="{theme["VIOLET2"]};{theme["CYAN"]};{theme["EMERALD"]};{theme["VIOLET2"]}" dur="10s" repeatCount="indefinite"/></stop>'
        f'<stop offset="1" stop-color="{theme["EMERALD"]}"><animate attributeName="stop-color" values="{theme["EMERALD"]};{theme["VIOLET2"]};{theme["CYAN"]};{theme["EMERALD"]}" dur="10s" repeatCount="indefinite"/></stop>'
        '</linearGradient></defs>',
        f'<text x="{MARGIN+2}" y="18" font-size="11" letter-spacing="2" fill="{theme["CYAN"]}">PROJECTS.LIST</text>',
        f'<text x="{MARGIN+130}" y="18" font-size="10" fill="{theme["DIM"]}">./projects.sh --all</text>',
        f'<line x1="{MARGIN}" y1="28" x2="{W-MARGIN}" y2="28" stroke="url(#{gid})" stroke-width="1.5" opacity="0.7"/>',
    ]
    for i, project in enumerate(projects):
        x = MARGIN + (i % 2) * (CARD_W + GAP + 4)
        y = 42 + (i // 2) * (CARD_H + GAP)
        parts.append(card(project, x, y, i, theme, DONUT_COLORS[theme_name]))
    if not projects:
        parts.append(f'<text x="20" y="80" font-size="13" fill="{theme["MUTED"]}">No projects configured yet — edit projects.json.</text>')
    parts.append('</svg>')
    return "".join(parts)


def main() -> None:
    source = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_INPUT
    output = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_OUTPUT
    projects = json.loads(source.read_text(encoding="utf-8"))
    output.mkdir(parents=True, exist_ok=True)
    for theme in THEMES:
        filename = "projects.svg" if theme == "dark" else "projects-light.svg"
        path = output / filename
        path.write_text(build(projects, theme), encoding="utf-8")
        print(f"wrote {path} ({len(projects)} projects)")


if __name__ == "__main__":
    main()
