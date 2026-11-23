"""用完整标题制作 1880×800 公众号横版 JPG，可选主图与署名。需要 Pillow。"""
import argparse
import io
import math
import re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps


def choose_font(path):
    for candidate in ([path] if path else ["msyhbd.ttc", "NotoSansCJK-Bold.ttc",
                                          "SourceHanSansCN-Bold.otf", "PingFang.ttc"]):
        try:
            ImageFont.truetype(candidate, 48)
            return candidate
        except OSError:
            continue
    raise ValueError("未找到可用字体，请用 --font 指定能显示标题文字的字体文件")


def wrap(text, font, width):
    """按实测宽度断行，尽量让英文单词、成对破折号和句末标点保持完整。"""
    lines, line = [], ""
    for token in re.findall(r"[A-Za-z0-9]+|——|\s+|.", text):
        if (line.strip() and font.getlength(line + token) > width
                and token not in "，。！？、：；）》”’」的" and not token.isspace()):
            lines.append(line.rstrip())
            line = ""
        line += token
    if line.strip():
        lines.append(line.rstrip())
    return lines


def make_cover(photo, title, output, author="", lines=None, font=None, focus=(.5, .5)):
    title = title.strip()
    if not title or output.suffix.lower() not in {".jpg", ".jpeg"}:
        raise ValueError("请提供完整标题，并用 .jpg 或 .jpeg 作为输出扩展名")
    if output.exists():
        raise FileExistsError(f"文件已存在，请另选文件名：{output}")
    if lines and (any(not line.strip() or len(line.splitlines()) > 1 for line in lines) or
                  not re.fullmatch(r"\s*".join(re.escape(line.strip()) for line in lines), title)):
        raise ValueError("--line 的文字与标点拼起来应和完整标题相同")
    if any(not 0 <= value <= 1 for value in focus):
        raise ValueError("--focus 的两个数均须在 0 到 1 之间")

    face = choose_font(font)
    panel_w, height = 760, 800
    canvas = Image.new("RGB", (1880, height), "#f3f0e8")
    if photo is not None:
        with Image.open(photo) as opened:
            source = ImageOps.exif_transpose(opened).convert("RGB")
            scale = max(panel_w / source.width, height / source.height) * 1.10
            crop_w, crop_h = panel_w / scale, height / scale
            # 焦点尽量靠近图文交界，保留方形分享裁切里的人物或物件。
            left = max(0, min(source.width - crop_w, source.width * focus[0] - crop_w * .76))
            top = max(0, min(source.height - crop_h, source.height * focus[1] - crop_h * .50))
            crop = (left, top, left + crop_w, top + crop_h)
            canvas.paste(source.resize((panel_w, height), Image.Resampling.LANCZOS, box=crop))

    draw = ImageDraw.Draw(canvas)
    if photo is None:
        x, width, horizontal = canvas.width // 2, 700, "m"
    else:
        x, width, horizontal = panel_w + 40, 522, "l"
    max_h = 485 if author else 565
    for size in range(124, 43, -2):
        regular = ImageFont.truetype(face, size)
        subtitle = ImageFont.truetype(face, round(size * .64))
        if lines:
            rows = lines
        else:
            lead, sep, tail = title.partition("——")
            wrap_width = 900
            if photo is None:
                # 平衡无图封面的标题行，使关键词尽量留在中央方形裁切区。
                text_width = regular.getlength(lead)
                row_count = max(1, math.ceil(text_width / 980))
                wrap_width = text_width / row_count + size * .53
            rows = wrap(lead, regular, wrap_width)
            if sep:
                rows += wrap(sep + tail, subtitle, 730)
        fonts = []
        for line in rows:
            base = subtitle if line.startswith("——") else regular
            fitted_size = int(base.size * min(1, width / max(1, base.getlength(line))))
            fonts.append(ImageFont.truetype(face, max(42, fitted_size)))
        heights = [int(f.size * 1.26) for f in fonts]
        if sum(heights) <= max_h and all(f.getlength(t) <= width for t, f in zip(rows, fonts)):
            break
    else:
        raise ValueError("标题过长，请以 --line 手动断行或另行排版，标题文字应保持完整")
    y = (height - sum(heights)) // 2 - (38 if author else 0)
    if photo is None:
        draw.line((x - 50, 94, x + 50, 94), fill="#a36a49", width=5)
    else:
        draw.line((x, 75, 1804, 75), fill="#b9ac97", width=2)
    for line, f, h in zip(rows, fonts, heights):
        draw.text((x, y + 2), line.strip(), font=f, anchor=horizontal + "t",
                  fill="#87533b" if line.startswith("——") else "#203540")
        y += h
    if author:
        author_font = ImageFont.truetype(face, 39)
        if author_font.getlength(author) > width:
            raise ValueError("署名过长，请另行排版")
        draw.text((x, 693), author, anchor=horizontal + "m", font=author_font, fill="#35444b")
    for quality in (92, 86, 80, 72, 62, 48):
        encoded = io.BytesIO()
        canvas.save(encoded, "JPEG", quality=quality, optimize=True)
        if encoded.tell() <= 1_000_000:
            break
    else:
        raise ValueError("无法在 1,000,000 字节之内编码，请调整封面排版或主图")
    file = output.open("xb")
    try:
        with file:
            file.write(encoded.getbuffer())
    except OSError:
        output.unlink(missing_ok=True)
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("photo", nargs="?", type=Path, help="可选主图路径；省略时生成文字封面")
    parser.add_argument("title", help="含标点的完整标题")
    parser.add_argument("output", type=Path, help="新 JPG 路径")
    parser.add_argument("--author", default="", help="可选署名")
    parser.add_argument("--line", action="append", help="按顺序重复该参数，可指定每行标题")
    parser.add_argument("--font", help="可选中文字型文件路径")
    parser.add_argument("--focus", nargs=2, type=float, default=(.5, .5), metavar=("X", "Y"),
                        help="主图焦点，左上为 0 0，右下为 1 1")
    args = parser.parse_args()
    try:
        make_cover(args.photo, args.title, args.output, args.author, args.line, args.font, args.focus)
    except (OSError, ValueError) as error:
        parser.exit(1, f"{error}\n")
