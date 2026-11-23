"""Read a construction-animation comparison CSV and SRT. Never writes media."""
import argparse
import csv
from fractions import Fraction
from pathlib import Path
import re
import sys
import unicodedata

LIMIT = Fraction(11, 2)
TIME = re.compile(r"(\d+):([0-5]\d):([0-5]\d),(\d{3})")
REQUIRED = "分镜编号 原字幕序号 新字幕 原朗读字数 新朗读字数 原字幕起毫秒 原字幕止毫秒 新起帧 新止帧含".split()


def milliseconds(text):
    match = TIME.fullmatch(text)
    if not match:
        raise ValueError(f"无效的 SRT 时间 {text}")
    h, m, s, ms = map(int, match.groups())
    return ((h * 60 + m) * 60 + s) * 1000 + ms


def cues(path):
    blocks = re.split(r"\n[ \t]*\n", path.read_text(encoding="utf-8-sig").strip("\n"))
    for i, block in enumerate(blocks, 1):
        lines = block.splitlines()
        if len(lines) < 3 or lines[0].strip() != str(i):
            raise ValueError(f"第 {i} 条 SRT 序号或正文缺失")
        start, end = lines[1].split(" --> ")
        yield milliseconds(start), milliseconds(end), "\n".join(lines[2:])


def rate(count, seconds):
    if count <= 0 or seconds <= 0:
        raise ValueError("朗读字数及区间时长须大于零")
    return Fraction(count) / seconds


def check(table, srt, fps, sample_rate):
    if fps <= 0 or sample_rate <= 0:
        raise ValueError("帧率和采样率须大于零")
    with table.open(encoding="utf-8-sig", newline="") as src:
        reader = csv.DictReader(src)
        fields = reader.fieldnames or []
        missing = set(REQUIRED) - set(fields)
        if missing:
            raise ValueError("CSV 缺少列 " + "、".join(sorted(missing)))
        def unique(pattern):
            matches = [key for key in fields if re.fullmatch(pattern, key)]
            if len(matches) != 1:
                raise ValueError(f"须唯一指定当前版本的列 {pattern}，找到 {matches}")
            return matches[0]
        syn = unique(r"(?:新|V\d+)合成倍率")
        post = unique(r"(?:新|V\d+)后期倍率")
        rows = list(reader)
    subs = list(cues(srt))
    if not rows or len(rows) != len(subs):
        raise ValueError(f"时间轴 {len(rows)} 条，SRT {len(subs)} 条")
    before = {}
    issues = []
    prev_end = 0
    peak = Fraction()
    for i, (row, (start, end, text)) in enumerate(zip(rows, subs), 1):
        label = f"{row['分镜编号']} 第 {i} 条"
        a, b = int(row["新起帧"]), int(row["新止帧含"])
        old_ms = int(row["原字幕止毫秒"]) - int(row["原字幕起毫秒"])
        orig = rate(int(row["原朗读字数"]), Fraction(old_ms, 1000))
        if orig > LIMIT:
            before[row["原字幕序号"]] = orig
        num = int(row["新朗读字数"])
        duration = (b - a + 1) / fps
        speed = rate(num, duration)
        peak = max(peak, speed)
        if a < 1 or a <= prev_end or end <= start:
            issues.append(f"{label} 时间区间无效或与前条重叠")
        prev_end = b
        if (abs(start - 1000 * (a - 1) / fps) > Fraction(1, 2)
                or abs(end - 1000 * b / fps) > Fraction(1, 2)):
            issues.append(f"{label} SRT 时码与帧表不一致")
        if text != row["新字幕"]:
            issues.append(f"{label} SRT 文字与定稿不一致")
        last = text.rstrip()[-1:]
        if not last or (unicodedata.category(last).startswith("P") and last not in "%％‰‱"):
            issues.append(f"{label} 字幕为空或带末尾标点")
        if speed > LIMIT:
            issues.append(f"{label} 显示区间 {float(speed):.5f} 字/秒超标")
        if Fraction(row[syn]) != 1 or Fraction(row[post]) != 1:
            issues.append(f"{label} 配音倍率不是 1.0")
        if "净音频采样数" in fields:
            audible = Fraction(int(row["净音频采样数"]), sample_rate)
            if rate(num, audible) > LIMIT:
                issues.append(f"{label} 净配音朗读速度超标")
            if "配音起采样" in fields:
                begin = Fraction(int(row["配音起采样"]), sample_rate)
                tol = 1 / Fraction(sample_rate)
                if begin < (a - 1) / fps - tol or begin + audible > b / fps + tol:
                    issues.append(f"{label} 配音越出字幕区间")
    flags = "、".join(f"{key}（{float(value):.5f}）" for key, value in before.items())
    print(f"原超标条目 {flags or '无'}")
    print(f"定稿 {len(subs)} 条，最高 {float(peak):.5f} 字/秒")
    for message in issues:
        print(message, file=sys.stderr)
    return int(bool(issues))


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("csv", type=Path)
    cli.add_argument("srt", type=Path)
    cli.add_argument("--fps", type=Fraction, required=True)
    cli.add_argument("--sample-rate", type=int, required=True,
                     help="配音主表的采样率，如 24000，不取 MP4 的 AAC 采样率")
    args = cli.parse_args()
    try:
        sys.exit(check(args.csv, args.srt, args.fps, args.sample_rate))
    except (OSError, ValueError, ZeroDivisionError, csv.Error) as error:
        cli.exit(2, f"读取或校验失败：{error}\n")
