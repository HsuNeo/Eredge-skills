"""Check skill names, entrypoints and local Markdown references; no dependencies."""
import argparse
from pathlib import Path
import re
import tempfile
from urllib.parse import unquote, urlsplit


def check(root):
    errors = []
    folders = sorted(p for p in root.iterdir() if p.is_dir())
    for folder in folders:
        entry = folder / 'SKILL.md'
        if not entry.is_file():
            errors.append(f'{folder.name}: missing SKILL.md')
            continue
        text = entry.read_text(encoding='utf-8-sig')
        head = re.match(r'\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)', text, re.S)
        if not head:
            errors.append(f'{folder.name}: missing frontmatter')
            continue
        name = re.search(r'(?m)^name:[ \t]*([^\r\n]+)', head[1])
        desc = re.search(r'(?m)^description:[ \t]*([^\r\n]+)', head[1])
        if not name or name[1].strip().strip('"\'') != folder.name:
            errors.append(f'{folder.name}: name differs from folder')
        if not desc or not desc[1].strip():
            errors.append(f'{folder.name}: empty description')
        for doc in folder.rglob('*.md'):
            for link in re.findall(r'\[[^\]]*\]\(([^)]+)\)', doc.read_text(encoding='utf-8-sig')):
                target = urlsplit(link.strip('<>'))
                if target.scheme or not target.path:
                    continue
                resolved = (doc.parent / unquote(target.path)).resolve()
                if not resolved.is_relative_to(folder.resolve()) or not resolved.is_file():
                    errors.append(f'{doc.relative_to(root)}: missing or external local reference {link}')
    return len(folders), errors


def self_test():
    with tempfile.TemporaryDirectory(prefix='eredge-skill-check-') as temp:
        root = Path(temp)
        folder = root / 'sample'
        folder.mkdir()
        entry = folder / 'SKILL.md'
        text = '---\nname: sample\ndescription: Check sample\n---\n[Example](example.md)\n'
        entry.write_text(text, encoding='utf-8')
        assert check(root)[1], 'missing references must fail'
        (folder / 'example.md').write_text('Example\n', encoding='utf-8')
        assert check(root) == (1, []), 'self-contained skill must pass'
        (root / 'outside.md').write_text('Outside\n', encoding='utf-8')
        entry.write_text(text.replace('example.md', '../outside.md'), encoding='utf-8')
        assert check(root)[1], 'references outside the skill must fail'
        entry.write_text(text.replace('name: sample', 'name: other'), encoding='utf-8')
        assert check(root)[1], 'wrong skill identity must fail'
    print('PASS: missing references, self-contained install, path bounds, skill identity')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--self-test', action='store_true')
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1] / 'skills')
    args = parser.parse_args()
    if args.self_test:
        self_test()
    else:
        count, errors = check(args.root)
        print('\n'.join(errors) if errors else f'PASS: {count} skill entrypoints and local references')
        raise SystemExit(bool(errors))
