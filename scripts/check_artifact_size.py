"""Check the exact TAR representation produced for GitHub Pages."""
from pathlib import Path
import argparse
import json
import os
import subprocess
import tempfile

LIMIT = 1_073_741_824


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('site', nargs='?', default='_site')
    parser.add_argument('--output', help='Keep the TAR at this path instead of a temporary file')
    args = parser.parse_args()
    site = Path(args.site).resolve()
    if not (site / 'index.html').is_file():
        raise SystemExit(f'Not a reading site: {site}')
    if args.output:
        artifact = Path(args.output).resolve()
        artifact.parent.mkdir(parents=True, exist_ok=True)
        cleanup = None
    else:
        cleanup = tempfile.TemporaryDirectory(prefix='pages-size-')
        artifact = Path(cleanup.name) / 'artifact.tar'
    try:
        # Match the official upload-pages-artifact tar behavior. Our site has
        # no hidden files or links, so no extra exclusions are required.
        tar = Path(os.environ.get('ProgramFiles', 'C:/Program Files')) / 'Git/usr/bin/tar.exe'
        executable = str(tar) if os.name == 'nt' and tar.is_file() else 'tar'
        subprocess.run([executable, '--force-local', '--dereference', '--hard-dereference', '--directory', site.as_posix(), '-cf', artifact.as_posix(), '.'], check=True)
        size = artifact.stat().st_size
        print(json.dumps({'tar_bytes': size, 'limit_bytes': LIMIT, 'remaining_bytes': LIMIT - size, 'within_limit': size < LIMIT}, indent=2))
        if size >= LIMIT:
            raise SystemExit('Pages artifact is at or above the 1 GiB limit')
    finally:
        if cleanup:
            cleanup.cleanup()


if __name__ == '__main__':
    main()
