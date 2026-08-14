#!/usr/bin/env python3
"""Generate the animated dark/light profile banners for Ashish Raj."""
from __future__ import annotations

import base64
import html
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMAGE = ROOT / "assets" / "ashish-dithered.png"

PROFILE = {
    "name": "Ashish Raj",
    "role": "Full-Stack Developer",
    "origin": "Khagaria, Bihar",
    "education": "Jaypee University of Information Technology",
    "status": "Building • Learning",
    "toolchain": "VS Code, Git, GitHub",
    "languages": "C, C++, Python, JavaScript",
    "frontend": "React",
    "backend": "Node.js, Express",
    "database": "PostgreSQL, MongoDB",
    "infra": "Vercel, Git",
    "email": "ashishraj140744@gmail.com",
    "linkedin": "ashish-raj-862020375",
    "github": "@ashishraj140744",
}

THEMES = {
    "dark": {
        "bg": "#070B16", "panel": "#0A101F", "bar": "#0B1222",
        "cyan": "#22D3EE", "violet": "#A78BFA", "violet2": "#7C3AED",
        "emerald": "#10B981", "text": "#F8FAFC", "muted": "#94A3B8",
        "dim": "#475569", "stroke": "rgba(255,255,255,0.10)",
        "photo": "#A78BFA", "accent_values": "#7C3AED;#22D3EE;#10B981;#7C3AED",
        "email_bg": "#4C1D95", "email_text": "#E9D5FF",
        "line": "rgba(148,163,184,0.35)",
    },
    "light": {
        "bg": "#F8FAFC", "panel": "#FFFFFF", "bar": "#F1F5F9",
        "cyan": "#0891B2", "violet": "#7C3AED", "violet2": "#6D28D9",
        "emerald": "#059669", "text": "#0F172A", "muted": "#475569",
        "dim": "#94A3B8", "stroke": "rgba(15,23,42,0.10)",
        "photo": "#6D28D9", "accent_values": "#6D28D9;#0891B2;#059669;#6D28D9",
        "email_bg": "#DBEAFE", "email_text": "#1D4ED8",
        "line": "rgba(15,23,42,0.25)",
    },
}

FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"


def esc(value: str) -> str:
    return html.escape(str(value), quote=True)


def data_uri(path: Path) -> str:
    raw = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{raw}"


def line_text(label: str, value: str, y: int, theme: dict, begin: float) -> str:
    # textLength keeps the terminal-style leader aligned across themes.
    return (
        f'<g opacity="1">'
        f'<animateTransform attributeName="transform" type="translate" values="-8 0;0 0" dur="0.4s" begin="{begin:.2f}s" fill="freeze"/>'
        f'<text x="470" y="{y}" font-size="14" textLength="655" lengthAdjust="spacingAndGlyphs" xml:space="preserve">'
        f'<tspan fill="{theme["cyan"]}">{esc(label)} </tspan>'
        f'<tspan fill="{theme["line"]}">{"." * max(12, 64-len(label)-len(value))}</tspan>'
        f'<tspan fill="{theme["text"]}" font-weight="600"> {esc(value)}</tspan>'
        f'</text></g>'
    )


def build(theme_name: str) -> str:
    t = THEMES[theme_name]
    img = data_uri(IMAGE)
    accent_id = f"accent-{theme_name}"
    clip_id = f"photo-clip-{theme_name}"

    lines = [
        ("Subject", PROFILE["name"], 162, 0.90),
        ("Role", PROFILE["role"], 185, 1.02),
        ("Origin", PROFILE["origin"], 208, 1.14),
        ("Education", PROFILE["education"], 231, 1.26),
        ("Status", PROFILE["status"], 254, 1.38),
        ("ToolChain", PROFILE["toolchain"], 277, 1.50),
        ("Core.Lang", PROFILE["languages"], 308, 1.72),
        ("Core.Frontend", PROFILE["frontend"], 331, 1.84),
        ("Core.Backend", PROFILE["backend"], 354, 1.96),
        ("Core.Database", PROFILE["database"], 377, 2.08),
        ("Core.Infra", PROFILE["infra"], 400, 2.20),
    ]

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="1180" height="610" viewBox="0 0 1180 610" '
        f'font-family="{FONT}" role="img" aria-label="Ashish Raj — profile.sh --live">',
        '<defs>',
        f'<linearGradient id="{accent_id}" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="{t["violet2"]}"><animate attributeName="stop-color" values="{t["accent_values"]}" dur="10s" repeatCount="indefinite"/></stop>'
        f'<stop offset="0.5" stop-color="{t["cyan"]}"><animate attributeName="stop-color" values="{t["cyan"]};{t["emerald"]};{t["violet2"]};{t["cyan"]}" dur="10s" repeatCount="indefinite"/></stop>'
        f'<stop offset="1" stop-color="{t["emerald"]}"><animate attributeName="stop-color" values="{t["emerald"]};{t["violet2"]};{t["cyan"]};{t["emerald"]}" dur="10s" repeatCount="indefinite"/></stop>'
        '</linearGradient>',
        f'<filter id="glow-{theme_name}" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="8"/></filter>',
        f'<filter id="glow3-{theme_name}" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="3"/></filter>',
        f'<filter id="txt-{theme_name}" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="0.9" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>',
        f'<clipPath id="{clip_id}"><rect x="36" y="84" width="400" height="492" rx="10"/></clipPath>',
        '</defs>',
        f'<rect x="2" y="2" width="1176" height="606" rx="18" fill="{t["bg"]}"/>',
        f'<rect x="2" y="2" width="1176" height="46" fill="{t["bar"]}"/>',
        f'<line x1="2" y1="48" x2="1178" y2="48" stroke="{t["stroke"]}"/>',
        '<circle cx="30" cy="25" r="5.5" fill="#ff5f56"/><circle cx="50" cy="25" r="5.5" fill="#ffbd2e"/><circle cx="70" cy="25" r="5.5" fill="#27c93f"/>',
        f'<text x="590" y="29" text-anchor="middle" font-size="12" fill="{t["muted"]}">{esc(PROFILE["email"])} - % ./profile.sh --live</text>',
        f'<text x="38" y="74" font-size="10" letter-spacing="3" fill="{t["dim"]}">VISUAL.MAP</text>',
        f'<rect x="36" y="84" width="400" height="492" rx="10" fill="none" stroke="{t["cyan"]}" stroke-width="2" opacity="0.45" filter="url(#glow3-{theme_name})"/>',
        f'<rect x="36" y="84" width="400" height="492" rx="10" fill="{t["panel"]}" stroke="{t["stroke"]}"/>',
        # Photo reveal + slow drift + breathing opacity. The attached image is already dithered.
        f'<g clip-path="url(#{clip_id})">',
        f'<image x="40" y="84" width="396" height="492" href="{img}" preserveAspectRatio="xMidYMid meet" opacity="1">'
        '<animate attributeName="opacity" values="1;0.92;1" dur="6s" begin="0.2s" repeatCount="indefinite"/>'
        '<animateTransform attributeName="transform" type="translate" values="0 0;3 -2;0 0" dur="8s" begin="0.2s" repeatCount="indefinite"/>'
        '</image>',
        # Scanline that makes the portrait feel alive without moving the whole image.
        f'<rect x="36" y="86" width="400" height="2" fill="{t["cyan"]}" opacity="0">'
        '<animate attributeName="y" values="86;574;86" dur="5.5s" begin="1.2s" repeatCount="indefinite"/>'
        '<animate attributeName="opacity" values="0;0.55;0" dur="5.5s" begin="1.2s" repeatCount="indefinite"/>'
        '</rect>',
        '</g>',
        f'<path d="M 50 84 L 36 84 L 36 98" fill="none" stroke="{t["cyan"]}" stroke-width="2" opacity="0.8"/>',
        f'<path d="M 422 84 L 436 84 L 436 98" fill="none" stroke="{t["cyan"]}" stroke-width="2" opacity="0.8"/>',
        f'<path d="M 50 576 L 36 576 L 36 562" fill="none" stroke="{t["cyan"]}" stroke-width="2" opacity="0.8"/>',
        f'<path d="M 422 576 L 436 576 L 436 562" fill="none" stroke="{t["cyan"]}" stroke-width="2" opacity="0.8"/>',
        f'<text x="470" y="106" font-size="13" letter-spacing="2" fill="{t["cyan"]}" filter="url(#txt-{theme_name})">SYSTEM.INFO</text>',
        f'<line x1="566" y1="102" x2="1061" y2="102" stroke="{t["stroke"]}"/>',
        f'<text x="1125" y="106" text-anchor="end" font-size="12" fill="#DC2626" font-weight="700"><tspan>●</tspan> LIVE<animate attributeName="opacity" values="1;0.25;1" dur="1.6s" repeatCount="indefinite"/></text>',
        f'<g opacity="1"><animate attributeName="opacity" values="1;0.9;1" dur="5s" begin="0.6s" repeatCount="indefinite"/><rect x="470" y="122" width="245" height="20" rx="4" fill="{t["email_bg"]}"/><text x="479" y="136" font-size="14" font-weight="700" fill="{t["email_text"]}">{esc(PROFILE["email"])}</text><line x1="725" y1="130" x2="1125" y2="130" stroke="{t["stroke"]}"/></g>',
    ]

    for label, value, y, begin in lines:
        parts.append(line_text(label, value, y, t, begin))

    parts += [
        f'<g opacity="1"><animate attributeName="opacity" values="1;0.9;1" dur="5s" begin="2.42s" repeatCount="indefinite"/><text x="470" y="431" font-size="14" textLength="655" lengthAdjust="spacingAndGlyphs" xml:space="preserve"><tspan fill="{t["muted"]}">- Contact </tspan><tspan fill="{t["line"]}">{"-" * 70}</tspan></text></g>',
        line_text("Grid.Mail", PROFILE["email"], 454, t, 2.54),
        line_text("Grid.LinkedIn", PROFILE["linkedin"], 477, t, 2.66),
        line_text("Grid.GitHub", PROFILE["github"], 500, t, 2.78),
        f'<g opacity="1"><animate attributeName="opacity" values="1;0.85;1" dur="1s" begin="3.02s" repeatCount="indefinite"/><text x="470" y="546" font-size="14" fill="{t["muted"]}">&#9656; More about me &amp; projects below in README &#8595; <tspan fill="{t["cyan"]}">&#9608;<animate attributeName="fill-opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/></tspan></text></g>',
        f'<rect x="3" y="3" width="1174" height="604" rx="17" fill="none" stroke="url(#{accent_id})" stroke-width="3" opacity="0.55" filter="url(#glow-{theme_name})"/>',
        f'<rect x="3" y="3" width="1174" height="604" rx="17" fill="none" stroke="url(#{accent_id})" stroke-width="1.6"/>',
        '</svg>',
    ]
    return "\n".join(parts)


def main() -> None:
    if not IMAGE.exists():
        raise SystemExit(f"Missing avatar: {IMAGE}")
    for theme in THEMES:
        out = ROOT / f"{theme}.svg"
        out.write_text(build(theme), encoding="utf-8")
        print(f"wrote {out}")


if __name__ == "__main__":
    main()
