"""Check public packaging, local Markdown links and accidental private artifacts."""
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SKIP = {'.git', '__pycache__', '.venv', 'node_modules', 'private', 'artifacts', 'dist', '.playwright-mcp'}


def main():
    problems = []
    for name in ['README.md', 'LICENSE', '.codex-plugin/plugin.json', '.mcp.json',
                 'skills/design-looker-report/SKILL.md', 'config/server.json']:
        if not (ROOT / name).is_file():
            problems.append(f'Missing {name}')
    for path in ROOT.rglob('*'):
        if not path.is_file() or SKIP.intersection(path.relative_to(ROOT).parts):
            continue
        if path.relative_to(ROOT).as_posix() in {'opencode.json', '.codex/config.toml', '.claude/settings.local.json'}:
            continue
        if path.suffix.lower() in {'.pdf', '.csv', '.png', '.jpg', '.zip'}:
            problems.append(f'Review private/binary artifact: {path.relative_to(ROOT)}')
            continue
        try:
            text = path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            problems.append(f'Unexpected binary: {path.relative_to(ROOT)}')
            continue
        if path.suffix == '.json':
            try:
                json.loads(text)
            except ValueError as exc:
                problems.append(f'Invalid JSON: {path.name}: {exc}')
        if re.search(r'https://(?:docs\.google\.com/spreadsheets/d/|(?:data|looker)studio\.google\.com/(?:u/\d+/)?reporting/)[A-Za-z0-9_-]{20,}', text):
            problems.append(f'Private report/Sheet URL: {path.relative_to(ROOT)}')
        personal_path = r'(?:C:/' + r'Users/|C:\\' + r'Users\\)[^\s<>]+'
        if re.search(personal_path, text):
            problems.append(f'Personal absolute path: {path.relative_to(ROOT)}')
        if path.suffix == '.md':
            for target in re.findall(r'\]\(([^)]+)\)', text):
                target = target.split('#')[0]
                if not target or '://' in target or target.startswith('mailto:'):
                    continue
                if not (path.parent / target).exists():
                    problems.append(f'Broken link: {path.relative_to(ROOT)} -> {target}')
    manifest = ROOT / '.codex-plugin/plugin.json'
    if manifest.exists():
        data = json.loads(manifest.read_text(encoding='utf-8'))
        if data['name'] != ROOT.name:
            problems.append('Plugin name must match directory name')
    if problems:
        print('\n'.join(problems))
        return 1
    print('PASS: public package, JSON, local links and artifact checks')
    return 0


if __name__ == '__main__':
    sys.exit(main())
