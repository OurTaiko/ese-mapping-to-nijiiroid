import argparse
import json
from pathlib import Path, PureWindowsPath


def main():
    root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description='Check mapped song files against an ESE/Songs directory.')
    parser.add_argument('--songs-root', type=Path, default=root.parent / 'ESE')
    args = parser.parse_args()
    if not args.songs_root.is_dir():
        parser.error(f'Songs directory does not exist: {args.songs_root}')
    data = json.loads((root / 'data.json').read_text(encoding='utf-8'))
    missing = []
    empty = 0
    for key, rel_path in data.items():
        if not rel_path:
            empty += 1
            continue
        path = PureWindowsPath(rel_path)
        if path.is_absolute() or path.drive or '..' in path.parts or not args.songs_root.joinpath(*path.parts).is_file():
            missing.append((key, rel_path))
    if missing:
        print(f'{len(missing)} missing paths out of {len(data) - empty} mapped paths:')
        for key, rel_path in missing:
            print(f'  [{key}] {rel_path}')
    else:
        print(f'All {len(data) - empty} mapped paths exist.')
    print(f'{empty} empty mappings skipped; {len(data)} total entries.')
    return 1 if missing else 0


if __name__ == '__main__':
    raise SystemExit(main())
