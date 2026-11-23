"""Render a standalone WeChat copy page from a UTF-8 article manifest."""
import argparse
import base64
import json
import re
from html import escape
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parents[1] / "assets" / "article.html"
PARAGRAPH = "margin:0 0 17px;font-size:17px;line-height:1.95;color:#29333e;letter-spacing:.25px;white-space:pre-line"
CAPTION = "margin:8px 3px 0;color:#596675;font-size:14px;line-height:1.7;text-align:center"


def required(obj, key):
    value = obj[key]
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must contain text")
    return value


def figure(block, base_dir, *, cover=False):
    path = base_dir / required(block, "src")
    if path.stat().st_size > 1_000_000:
        raise ValueError(f"Prepare a copy of {path.name} at or below 1,000,000 bytes")
    data = path.read_bytes()
    if data.startswith(b"\xff\xd8\xff"):
        mime = "image/jpeg"
    elif data.startswith(b"\x89PNG\r\n\x1a\n"):
        mime = "image/png"
    else:
        raise ValueError(f"Use a PNG or JPEG for {path.name}")
    alt = escape(required(block, "alt"), quote=True)
    image = base64.b64encode(data).decode("ascii")
    caption = escape(block.get("caption", ""))
    note = f'<p style="{CAPTION}">{caption}</p>' if caption else ""
    margin = "0 0 23px" if cover else "22px 0 26px"
    element_id = ' id="article-cover"' if cover else ""
    return (f'<section{element_id} style="margin:{margin}"><img alt="{alt}" '
            f'src="data:{mime};base64,{image}" style="display:block;width:100%;height:auto;border:0">'
            f'{note}</section>')


def render(manifest):
    article = json.loads(manifest.read_text(encoding="utf-8-sig"))
    title = escape(required(article, "title"))
    summary = escape(required(article, "summary"))
    author = escape(article.get("author", ""))
    layout = article.get("layout", "article")
    if layout not in ("article", "report"):
        raise ValueError("layout must be article or report")
    accent = article.get("accent", "#0D2947" if layout == "report" else "#21364b")
    if not re.fullmatch(r"#[\da-fA-F]{6}", accent):
        raise ValueError("accent must be a six-digit hex color")
    styles = {
        "p": PARAGRAPH,
        "quote": f"margin:18px 0;padding:8px 14px;border-left:3px solid {accent};color:#43505c;line-height:1.85;white-space:pre-line",
        "h2": f"margin:34px 0 15px;padding-left:12px;border-left:4px solid {accent};font-size:23px;line-height:1.5;color:{accent}",
        "h3": f"margin:26px 0 12px;font-size:20px;line-height:1.5;color:{accent}",
    }
    if layout == "report":
        styles["h2"] = (f"margin:35px 0 17px;padding:19px 0 0;border-top:1px solid #d7e4ef;"
                        f"font-size:26px;font-weight:700;line-height:1.4;color:{accent};text-align:center")
        styles["h3"] = (f"margin:28px 0 12px;font-size:22px;font-weight:700;"
                        f"line-height:1.4;color:{accent};text-align:center")
    blocks = article["blocks"]
    if not isinstance(blocks, list) or not blocks:
        raise ValueError("blocks must be a nonempty list")
    body = []
    if "cover" in article:
        body.append(figure(article["cover"], manifest.parent, cover=True))
    for block in blocks:
        tag = block["type"]
        if tag == "image":
            body.append(figure(block, manifest.parent))
        elif tag in ("ul", "ol"):
            items = block.get("items")
            if not isinstance(items, list) or not items or not all(isinstance(item, str) and item.strip() for item in items):
                raise ValueError(f"{tag} requires a nonempty list of text items")
            rows = "".join(f'<li style="margin:0 0 6px">{escape(item)}</li>' for item in items)
            body.append(f'<{tag} style="margin:0 0 17px;padding-left:1.6em;line-height:1.95">{rows}</{tag}>')
        elif tag in styles:
            text = escape(required(block, "text"))
            element = "blockquote" if tag == "quote" else tag
            body.append(f'<{element} style="{styles[tag]}">{text}</{element}>')
        else:
            raise ValueError(f"Unknown block type: {tag}")
    values = {
        "TITLE": title, "SUMMARY": summary, "ACCENT": accent, "BODY": "\n".join(body), "LAYOUT": layout,
        "BYLINE": f'<p class="byline">作者｜{author}</p>' if author else "",
    }
    return re.sub(r"@@([A-Z]+)@@", lambda m: values[m[1]], TEMPLATE.read_text("utf-8"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    markup = render(args.manifest)
    with args.output.open("x", encoding="utf-8") as output:
        output.write(markup)


if __name__ == "__main__":
    main()
