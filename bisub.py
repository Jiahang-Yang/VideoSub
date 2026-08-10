"""
中英双语 ASS 字幕生成器
读取两份 SRT（中文 / 英文），合并输出为单行双语的 ASS 字幕。
"""

import bisect
import sys
import os

import pysubs2
from pysubs2 import SSAFile, SSAEvent, SSAStyle, Color

SRT_CN = None
SRT_EN = None
OUTPUT_ASS = None

ALIGN_MODE = "index"
TIME_THRESHOLD_MS = 500

PLAY_RES_X = 1920
PLAY_RES_Y = 1080

STYLE = {
    "Fontname": "Microsoft YaHei",
    "Fontsize": 70,
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
    "Outline": 3,
    "Shadow": 0,
    "Alignment": 2,
    "MarginL": 10,
    "MarginR": 10,
    "MarginV": 10,
    "Encoding": 1,
}

TAG_CN = r""
TAG_EN = r"{\fs50\bord2.5}"



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


def _align_by_index(cn_events, en_events):
    if len(cn_events) != len(en_events):
        msg = (
            f"索引对齐要求两文件行数一致，但中文 {len(cn_events)} 行，"
            f"英文 {len(en_events)} 行。\n请改用 ALIGN_MODE='time'。"
        )
        raise ValueError(msg)
    return zip(cn_events, en_events)


def _align_by_time(cn_events, en_events, threshold_ms):
    en_starts = [(e.start, e) for e in en_events]
    en_starts.sort(key=lambda x: x[0])
    starts = [s for s, _ in en_starts]
    en_map = {s: e for s, e in en_starts}

    pairs = []
    unmatched = 0
    for ce in cn_events:
        idx = bisect.bisect_left(starts, ce.start)
        best = None
        best_diff = float("inf")
        for i in (idx - 1, idx, idx + 1):
            if 0 <= i < len(starts):
                d = abs(starts[i] - ce.start)
                if d < best_diff:
                    best_diff = d
                    best = en_map[starts[i]]
        if best is not None and best_diff <= threshold_ms:
            pairs.append((ce, best))
        else:
            pairs.append((ce, None))
            unmatched += 1
    return pairs


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
        print("请提供项目名: python bisub.py <ProjectName>")
        sys.exit(1)

    name = name.strip("\ufeff")

    folder = os.path.join(".", name)
    global SRT_CN, SRT_EN, OUTPUT_ASS
    SRT_CN = os.path.join(folder, f"{name}.zh.srt")
    SRT_EN = os.path.join(folder, f"{name}.en.srt")
    OUTPUT_ASS = os.path.join(folder, f"{name}.ass")


def main():
    _resolve_project()
    assert SRT_CN is not None
    assert SRT_EN is not None
    cn_sub = pysubs2.load(SRT_CN, encoding="utf-8")
    en_sub = pysubs2.load(SRT_EN, encoding="utf-8")

    cn_events = list(cn_sub.events)
    en_events = list(en_sub.events)

    if ALIGN_MODE == "index":
        pairs = _align_by_index(cn_events, en_events)
    else:
        pairs = _align_by_time(cn_events, en_events, TIME_THRESHOLD_MS)

    out = SSAFile()
    out.styles["Subtitles"] = _build_style(STYLE)
    out.info["WrapStyle"] = "0"
    out.info["PlayResX"] = str(PLAY_RES_X)
    out.info["PlayResY"] = str(PLAY_RES_Y)

    miss = 0
    for ce, ee in pairs:
        cn_text = ce.plaintext.replace(r"\N", " ").replace(r"\n", " ").replace("\n", " ")
        if ee is None:
            en_text = ""
            miss += 1
        else:
            en_text = ee.plaintext.replace(r"\N", " ").replace(r"\n", " ").replace("\n", " ")

        combined = f"{TAG_CN}{cn_text}\\N{TAG_EN}{en_text}"
        event = SSAEvent(
            start=ce.start,
            end=ce.end,
            text=combined,
            style="Subtitles",
        )
        out.events.append(event)

    assert OUTPUT_ASS is not None
    out.save(OUTPUT_ASS, encoding="utf-8")

    print(f"完成！共生成 {len(out.events)} 行字幕")
    if ALIGN_MODE == "time" and miss:
        print(f"警告：{miss} 条中文未匹配到对应英文字幕（超时或超出阈值）")
    print(f"输出文件: {OUTPUT_ASS}")


if __name__ == "__main__":
    main()
