#!/usr/bin/env python3
"""Render ChronoRAG-G public architecture diagrams from deterministic JSON sources."""

from __future__ import annotations

import json
from pathlib import Path
import textwrap
from typing import Iterable

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.patches import FancyArrowPatch, Rectangle

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "docs" / "architecture" / "sources"
FIGURE_DIR = ROOT / "docs" / "architecture" / "figures"
DEFAULT_WIDTH = 2000
DEFAULT_HEIGHT = 1200
DPI = 100
NODE_FONT = 15
TITLE_FONT = 28
GROUP_FONT = 19
NOTE_FONT = 14
FOOTNOTE_FONT = 13
NODE_PADDING = 14
COLORS = {
    "navy": "#17324D",
    "blue": "#2A5D84",
    "light_blue": "#EAF2F8",
    "gold": "#C89B3C",
    "dark_text": "#1F2933",
    "mid_text": "#5B6770",
    "border": "#D8E0E7",
    "neutral": "#F8FAFC",
}


RectTuple = tuple[float, float, float, float]
Point = tuple[float, float]


def canvas_size(spec: dict[str, object]) -> tuple[int, int]:
    canvas = spec.get("canvas")
    if isinstance(canvas, dict):
        return int(canvas.get("width", DEFAULT_WIDTH)), int(canvas.get("height", DEFAULT_HEIGHT))
    return DEFAULT_WIDTH, DEFAULT_HEIGHT


def rect(item: dict[str, object]) -> RectTuple:
    return (float(item["x"]), float(item["y"]), float(item["w"]), float(item["h"]))


def rect_right(box: RectTuple) -> float:
    return box[0] + box[2]


def rect_bottom(box: RectTuple) -> float:
    return box[1] + box[3]


def rects_intersect(a: RectTuple, b: RectTuple, margin: float = 0.0) -> bool:
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return not (
        ax + aw + margin <= bx
        or bx + bw + margin <= ax
        or ay + ah + margin <= by
        or by + bh + margin <= ay
    )


def center(node: dict[str, object]) -> Point:
    return (float(node["x"]) + float(node["w"]) / 2, float(node["y"]) + float(node["h"]) / 2)


def wrapped_lines(label: str, width_px: float, fontsize: int, padding: float = NODE_PADDING) -> list[str]:
    available = max(12, width_px - 2 * padding)
    chars = max(8, int(available / (fontsize * 0.70)))
    lines: list[str] = []
    for part in str(label).split("\n"):
        lines.extend(textwrap.wrap(part, width=chars, break_long_words=False) or [""])
    return lines


def wrap(label: str, width_px: float, fontsize: int, padding: float = NODE_PADDING) -> str:
    return "\n".join(wrapped_lines(label, width_px, fontsize, padding))


def text_overflows_box(label: str, width_px: float, height_px: float, fontsize: int, padding: float = NODE_PADDING) -> bool:
    available_w = max(12.0, width_px - 2 * padding)
    available_h = max(12.0, height_px - 2 * padding)
    lines = wrapped_lines(label, width_px, fontsize, padding)
    longest = max((len(line) for line in lines), default=0)
    estimated_w = longest * fontsize * 0.70
    estimated_h = len(lines) * fontsize * 1.24
    return estimated_w > available_w or estimated_h > available_h


def group_title_rect(group: dict[str, object]) -> RectTuple:
    label = str(group["label"])
    lines = wrapped_lines(label, float(group["w"]) - 36, GROUP_FONT, 0)
    width = min(float(group["w"]) - 36, max(90.0, max((len(line) for line in lines), default=0) * GROUP_FONT * 0.70))
    height = max(34.0, len(lines) * GROUP_FONT * 1.2)
    return (float(group["x"]) + 18, float(group["y"]) + 11, width, height)


def edge_points(a: dict[str, object], b: dict[str, object]) -> tuple[Point, Point]:
    ax, ay = center(a)
    bx, by = center(b)
    dx = bx - ax
    dy = by - ay
    if abs(dx) >= abs(dy):
        start = (ax + (float(a["w"]) / 2) * (1 if dx >= 0 else -1), ay)
        end = (bx - (float(b["w"]) / 2) * (1 if dx >= 0 else -1), by)
    else:
        start = (ax, ay + (float(a["h"]) / 2) * (1 if dy >= 0 else -1))
        end = (bx, by - (float(b["h"]) / 2) * (1 if dy >= 0 else -1))
    return start, end


def default_route(a: dict[str, object], b: dict[str, object]) -> list[Point]:
    start, end = edge_points(a, b)
    if abs(start[0] - end[0]) < 0.01 or abs(start[1] - end[1]) < 0.01:
        return [start, end]
    mid_x = (start[0] + end[0]) / 2
    return [start, (mid_x, start[1]), (mid_x, end[1]), end]


def route_points(arrow: object, nodes: dict[str, dict[str, object]]) -> tuple[str, str, list[Point]]:
    if isinstance(arrow, dict):
        source = str(arrow["from"])
        target = str(arrow["to"])
        if "route" in arrow:
            return source, target, [(float(x), float(y)) for x, y in arrow["route"]]  # type: ignore[misc]
        return source, target, default_route(nodes[source], nodes[target])
    source, target = arrow  # type: ignore[misc]
    source = str(source)
    target = str(target)
    return source, target, default_route(nodes[source], nodes[target])


def segment_intersects_rect(a: Point, b: Point, box: RectTuple) -> bool:
    x, y, w, h = box
    x1, y1 = a
    x2, y2 = b
    eps = 1e-6
    if abs(x1 - x2) < eps:
        px = x1
        if not (x < px < x + w):
            return False
        lo, hi = sorted((y1, y2))
        return max(lo, y) < min(hi, y + h)
    if abs(y1 - y2) < eps:
        py = y1
        if not (y < py < y + h):
            return False
        lo, hi = sorted((x1, x2))
        return max(lo, x) < min(hi, x + w)
    # Conservative fallback for unexpected non-orthogonal routes.
    min_x, max_x = sorted((x1, x2))
    min_y, max_y = sorted((y1, y2))
    return rects_intersect((min_x, min_y, max_x - min_x, max_y - min_y), box)


def preflight(spec: dict[str, object]) -> dict[str, object]:
    width, height = canvas_size(spec)
    groups = list(spec.get("groups", []))
    nodes_list = list(spec.get("nodes", []))
    nodes = {str(item["id"]): item for item in nodes_list}
    counts = {
        "node_overlaps": 0,
        "group_title_overlaps": 0,
        "text_overflow_boxes": 0,
        "arrow_nonendpoint_node_intersections": 0,
        "canvas_overflow_items": 0,
    }
    details: dict[str, list[object]] = {key: [] for key in counts}

    for i, a in enumerate(nodes_list):
        a_rect = rect(a)
        for b in nodes_list[i + 1 :]:
            if rects_intersect(a_rect, rect(b), margin=0):
                counts["node_overlaps"] += 1
                details["node_overlaps"].append([a["id"], b["id"]])

    title_rects = [(str(group["label"]), group_title_rect(group)) for group in groups]
    for i, (label, a_rect) in enumerate(title_rects):
        for other_label, b_rect in title_rects[i + 1 :]:
            if rects_intersect(a_rect, b_rect, margin=0):
                counts["group_title_overlaps"] += 1
                details["group_title_overlaps"].append([label, other_label])
    for label, title_box in title_rects:
        for node in nodes_list:
            if rects_intersect(title_box, rect(node), margin=0):
                counts["group_title_overlaps"] += 1
                details["group_title_overlaps"].append([label, node["id"]])

    for node in nodes_list:
        fontsize = int(node.get("fontsize", NODE_FONT))
        if text_overflows_box(str(node["label"]), float(node["w"]), float(node["h"]), fontsize):
            counts["text_overflow_boxes"] += 1
            details["text_overflow_boxes"].append(node["id"])

    notes = list(spec.get("notes", []))
    if notes:
        note_box = spec.get("note_box", {})
        if not isinstance(note_box, dict):
            note_box = {}
        note_w = float(note_box.get("w", width - 180))
        note_h = float(note_box.get("h", 170))
        note_text = "\n".join("- " + str(note) for note in notes)
        if text_overflows_box(note_text, note_w - 44, note_h - 54, NOTE_FONT, 0):
            counts["text_overflow_boxes"] += 1
            details["text_overflow_boxes"].append("public_notes")

    for group in groups:
        x, y, w, h = rect(group)
        if x < 0 or y < 0 or x + w > width or y + h > height:
            counts["canvas_overflow_items"] += 1
            details["canvas_overflow_items"].append(group["label"])
    for node in nodes_list:
        x, y, w, h = rect(node)
        if x < 0 or y < 0 or x + w > width or y + h > height:
            counts["canvas_overflow_items"] += 1
            details["canvas_overflow_items"].append(node["id"])

    for arrow in spec.get("arrows", []):
        source, target, points = route_points(arrow, nodes)
        for point in points:
            if point[0] < 0 or point[1] < 0 or point[0] > width or point[1] > height:
                counts["canvas_overflow_items"] += 1
                details["canvas_overflow_items"].append([source, target, point])
        for start, end in zip(points, points[1:]):
            for node_id, node in nodes.items():
                if node_id in {source, target}:
                    continue
                if segment_intersects_rect(start, end, rect(node)):
                    counts["arrow_nonendpoint_node_intersections"] += 1
                    details["arrow_nonendpoint_node_intersections"].append([source, target, node_id])

    return {
        "stem": spec["stem"],
        "canvas": {"width": width, "height": height},
        "counts": counts,
        "details": details,
        "status": "PASS" if all(value == 0 for value in counts.values()) else "FAIL",
    }


def draw_box(ax, item: dict[str, object], fontsize: int = NODE_FONT, edge: str = COLORS["blue"]) -> None:
    fontsize = int(item.get("fontsize", fontsize))
    rect_patch = Rectangle(
        (float(item["x"]), float(item["y"])),
        float(item["w"]),
        float(item["h"]),
        linewidth=1.6,
        edgecolor=edge,
        facecolor=str(item.get("fill", COLORS["light_blue"])),
    )
    ax.add_patch(rect_patch)
    ax.text(
        float(item["x"]) + float(item["w"]) / 2,
        float(item["y"]) + float(item["h"]) / 2,
        wrap(str(item["label"]), float(item["w"]), fontsize),
        ha="center",
        va="center",
        fontsize=fontsize,
        color=COLORS["dark_text"],
        family="DejaVu Sans",
        linespacing=1.18,
    )


def draw_arrow(ax, points: Iterable[Point]) -> None:
    route = list(points)
    if len(route) < 2:
        return
    for start, end in zip(route[:-2], route[1:-1]):
        ax.plot([start[0], end[0]], [start[1], end[1]], color=COLORS["blue"], linewidth=1.5)
    arrow = FancyArrowPatch(
        route[-2],
        route[-1],
        arrowstyle="-|>",
        mutation_scale=16,
        linewidth=1.5,
        color=COLORS["blue"],
        shrinkA=0,
        shrinkB=0,
    )
    ax.add_patch(arrow)


def draw(spec: dict[str, object]) -> dict[str, object]:
    report = preflight(spec)
    if report["status"] != "PASS":
        raise ValueError(json.dumps(report, indent=2, sort_keys=True))

    rcParams["svg.fonttype"] = "none"
    rcParams["pdf.fonttype"] = 42
    rcParams["font.family"] = "DejaVu Sans"
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    width, height = canvas_size(spec)
    fig = plt.figure(figsize=(width / DPI, height / DPI), dpi=DPI)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, width)
    ax.set_ylim(height, 0)
    ax.axis("off")
    ax.add_patch(Rectangle((0, 0), width, height, facecolor="white", edgecolor="none"))
    ax.text(70, 70, str(spec["title"]), fontsize=TITLE_FONT, color=COLORS["navy"], weight="bold", va="top", family="DejaVu Sans")
    ax.plot([70, width - 70], [105, 105], color=COLORS["gold"], linewidth=3)

    for group in spec.get("groups", []):
        group_rect = Rectangle(
            (float(group["x"]), float(group["y"])),
            float(group["w"]),
            float(group["h"]),
            linewidth=1.4,
            edgecolor=COLORS["border"],
            facecolor=COLORS["neutral"],
        )
        ax.add_patch(group_rect)
        group_label = wrap(str(group["label"]), float(group["w"]) - 36, GROUP_FONT, 0)
        ax.text(
            float(group["x"]) + 18,
            float(group["y"]) + 18,
            group_label,
            fontsize=GROUP_FONT,
            color=COLORS["blue"],
            weight="bold",
            va="top",
            family="DejaVu Sans",
            linespacing=1.12,
        )

    nodes = {str(item["id"]): item for item in spec.get("nodes", [])}
    for item in spec.get("nodes", []):
        draw_box(ax, item)

    for arrow in spec.get("arrows", []):
        source, target, points = route_points(arrow, nodes)
        if source in nodes and target in nodes:
            draw_arrow(ax, points)

    notes = list(spec.get("notes", []))
    if notes:
        note_box = spec.get("note_box", {})
        if not isinstance(note_box, dict):
            note_box = {}
        note_x = float(note_box.get("x", 90))
        note_y = float(note_box.get("y", height - 300))
        note_w = float(note_box.get("w", width - 180))
        note_h = float(note_box.get("h", 190))
        ax.add_patch(Rectangle((note_x, note_y), note_w, note_h, linewidth=1.2, edgecolor=COLORS["border"], facecolor="#FFFFFF"))
        ax.text(note_x + 22, note_y + 28, "Public notes", fontsize=18, color=COLORS["blue"], weight="bold", va="top", family="DejaVu Sans")
        y = note_y + 66
        for note in notes:
            lines = wrap(str(note), note_w - 52, NOTE_FONT, 0)
            ax.text(note_x + 26, y, "- " + lines, fontsize=NOTE_FONT, color=COLORS["mid_text"], va="top", family="DejaVu Sans", linespacing=1.15)
            y += max(36, (lines.count("\n") + 1) * NOTE_FONT * 1.28 + 14)

    ax.text(
        70,
        height - 42,
        "Public research abstraction: synthetic labels and aggregate metrics only.",
        fontsize=FOOTNOTE_FONT,
        color=COLORS["mid_text"],
        family="DejaVu Sans",
    )
    stem = str(spec["stem"])
    metadata = {"Creator": "ChronoRAG-G public deterministic renderer", "Date": None}
    for ext in ("svg", "png", "pdf"):
        fig.savefig(FIGURE_DIR / f"{stem}.{ext}", format=ext, dpi=DPI, metadata=metadata)
    plt.close(fig)
    return report


def main() -> int:
    reports = []
    for source in sorted(SOURCE_DIR.glob("*.json")):
        reports.append(draw(json.loads(source.read_text(encoding="utf-8"))))
    print(json.dumps({"status": "PASS", "preflight": reports}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
