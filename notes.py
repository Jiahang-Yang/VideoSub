"""
将 notes.srt 转换为顶端对齐的 notes.ass
读取项目目录下的 notes.srt，生成独立的 notes.ass 字幕文件。
"""

import sys
import os

import pysubs2
from pysubs2 import SSAFile, SSAEvent, SSAStyle, Color

NOTES_STYLE = {
    "Fontname": "Microsoft YaHei",
    "Fontsize": 50,
    "PrimaryColour": "&H00FFFFFF",
    "SecondaryColour": "&H000000FF",
    "OutlineColour": "&H00000000",
    "BackColour": "&H64000000",
    "Bold": False,
    "Italic": False,
    "Underline": False,
    "StrikeOut": False,
    "ScaleX": 100,
    "ScaleY": 100,
    "Spacing": 0,
    "Angle": 0,
    "BorderStyle": 1,
    "Outline": 2,
    "Shadow": 0,
    "Alignment": 8,
    "MarginL": 10,
    "MarginR": 10,
    "MarginV": 10,
    "Encoding": 1,
}

TAG_NOTE = r"{\fad(500,500)}"


def _parse_ass_color(raw: str) -> Color:
    h = raw.strip().lstrip("&H").lstrip("&h")
    if len(h) == 6:
        h = "00" + h
    a = int(h[0:2], 16)
    b = int(h[2:4], 16)
    g = int(h[4:6], 16)
    r = int(h[6:8], 16)
    return Color(r, g, b, a)


def _build_style(cfg: dict) -> SSAStyle:
    s = SSAStyle()
    s.fontname = cfg["Fontname"]
    s.fontsize = cfg["Fontsize"]
    s.bold = bool(cfg["Bold"])
    s.italic = bool(cfg["Italic"])
    s.underline = bool(cfg["Underline"])
    s.strikeout = bool(cfg["StrikeOut"])
    s.scalex = cfg["ScaleX"]
    s.scaley = cfg["ScaleY"]
    s.spacing = cfg["Spacing"]
    s.angle = cfg["Angle"]
    s.borderstyle = cfg["BorderStyle"]
    s.outline = cfg["Outline"]
    s.shadow = cfg["Shadow"]
    s.alignment = cfg["Alignment"]
    s.marginl = cfg["MarginL"]
    s.marginr = cfg["MarginR"]
    s.marginv = cfg["MarginV"]
    s.encoding = cfg["Encoding"]
    s.primarycolor = _parse_ass_color(cfg["PrimaryColour"])
    s.secondarycolor = _parse_ass_color(cfg["SecondaryColour"])
    s.outlinecolor = _parse_ass_color(cfg["OutlineColour"])
    s.backcolor = _parse_ass_color(cfg["BackColour"])
    s.tertiarycolor = _parse_ass_color(cfg["BackColour"])
    return s


def _resolve_project():
    name = None
    if len(sys.argv) > 1:
        name = sys.argv[1]
    else:
        try:
            with open("current.txt", encoding="utf-8") as f:
                name = f.readline().strip()
        except FileNotFoundError:
            pass
    if not name:
        print("请提供项目名: python notes.py <ProjectName>")
        sys.exit(1)

    name = name.strip("\ufeff")
    return name


def main():
    name = _resolve_project()
    folder = os.path.join(".", name)
    notes_srt = os.path.join(folder, "notes.srt")
    notes_ass = os.path.join(folder, "notes.ass")

    if not os.path.exists(notes_srt):
        print("没有 notes.srt，无需处理")
        return

    notes_sub = pysubs2.load(notes_srt, encoding="utf-8")

    out = SSAFile()
    out.styles["Notes"] = _build_style(NOTES_STYLE)
    out.info["WrapStyle"] = "0"
    out.info["PlayResX"] = "1920"
    out.info["PlayResY"] = "1080"

    for event in notes_sub.events:
        text = event.plaintext.replace("\n", " ").replace(r"\N", " ")
        out.events.append(SSAEvent(
            start=event.start,
            end=event.end,
            text=f"{TAG_NOTE}{text}",
            style="Notes",
        ))

    out.save(notes_ass, encoding="utf-8")

    print(f"{len(notes_sub.events)} 条注释已写入 {notes_ass}")


if __name__ == "__main__":
    main()
