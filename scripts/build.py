"""Validate all local references, then prepare the GitHub Pages artifact.

Only Python's standard library is required. Run from the repository root:
    python scripts/build.py [--check-only]
"""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import argparse
import json
import re
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'site'
OUTPUT = ROOT / '_site'
LIMIT = 1_073_741_824


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.references = []
        self.ids = set()
        self.images = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get('id'):
            self.ids.add(attrs['id'])
        if tag == 'a' and attrs.get('name'):
            self.ids.add(attrs['name'])
        for name in ('href', 'src', 'poster', 'data'):
            if attrs.get(name):
                self.references.append(attrs[name])
        if attrs.get('srcset'):
            self.references.extend(part.strip().split()[0] for part in attrs['srcset'].split(',') if part.strip())
        if attrs.get('style'):
            self.references.extend(re.findall(r'url\([\"\']?([^\)\"\']+)', attrs['style']))
        if tag == 'img':
            self.images += 1


def validate():
    errors = []
    files = sorted(p for p in SITE.rglob('*') if p.is_file())
    if not (SITE / 'index.html').is_file():
        errors.append('Missing site/index.html')
    if any(p.is_symlink() for p in SITE.rglob('*')):
        errors.append('Symbolic links are not allowed in the Pages artifact')
    forbidden = [p for p in files if p.suffix.lower() in {'.zip', '.pdf'}]
    if forbidden:
        errors.append('Unexpected large download archives in site/')
    pages = {}
    for page in sorted(SITE.rglob('*.html')):
        parser = PageParser()
        parser.feed(page.read_text(encoding='utf-8'))
        pages[page.resolve()] = parser
    if len(pages) != 138:
        errors.append(f'Expected 138 HTML pages, found {len(pages)}')
    image_files = list((SITE / 'assets' / 'images').iterdir())
    if len(image_files) != 819:
        errors.append(f'Expected 819 image assets, found {len(image_files)}')
    checked_references = 0
    references = [(page, reference) for page, parser in pages.items() for reference in parser.references]
    for css in SITE.rglob('*.css'):
        references.extend((css, reference) for reference in re.findall(r'url\([\"\']?([^\)\"\']+)', css.read_text(encoding='utf-8')))
    for source, reference in references:
        parsed = urlsplit(reference)
        if parsed.scheme or parsed.netloc or reference.startswith('//'):
            continue
        if parsed.path.startswith('/'):
            errors.append(f'{source.relative_to(SITE)}: root-absolute URL breaks project Pages: {reference}')
            continue
        target = (source.parent / unquote(parsed.path)).resolve() if parsed.path else source.resolve()
        if target.is_dir():
            target = target / 'index.html'
        if not target.is_relative_to(SITE.resolve()):
            errors.append(f'{source.relative_to(SITE)}: URL escapes site: {reference}')
        elif not target.is_file():
            errors.append(f'{source.relative_to(SITE)}: missing reference: {reference}')
        elif parsed.fragment and target in pages and unquote(parsed.fragment) not in pages[target].ids:
            errors.append(f'{source.relative_to(SITE)}: missing anchor: {reference}')
        checked_references += 1
    byte_count = sum(p.stat().st_size for p in files)
    # Include conservative TAR headers, padding, and long filename records.
    estimated_artifact_bytes = sum(((p.stat().st_size + 511) // 512) * 512 + 2048 for p in files) + 1048576
    if estimated_artifact_bytes >= LIMIT:
        errors.append(f'Estimated Pages archive exceeds 1 GiB: {estimated_artifact_bytes:,} bytes')
    report = {
        'html_pages': len(pages), 'image_assets': len(image_files),
        'image_references': sum(p.images for p in pages.values()),
        'checked_local_references': checked_references, 'site_bytes': byte_count,
        'estimated_artifact_bytes': estimated_artifact_bytes, 'limit_bytes': LIMIT,
        'errors': sorted(set(errors)),
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if errors:
        sys.exit(1)
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check-only', action='store_true')
    args = parser.parse_args()
    validate()
    if not args.check_only:
        if OUTPUT.exists():
            if OUTPUT.resolve().parent != ROOT.resolve() or OUTPUT.name != '_site':
                raise RuntimeError('Refusing to replace an unexpected output directory')
            shutil.rmtree(OUTPUT)
        shutil.copytree(SITE, OUTPUT)
        print('Validated site copied to _site/')


if __name__ == '__main__':
    main()
