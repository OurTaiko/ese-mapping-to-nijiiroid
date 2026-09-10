"""Migrate path punctuation to match ESE b8806607; preserve spaces and extensions."""
import argparse
import re
from pathlib import Path, PureWindowsPath
from main import load_data, save_data


def clean_path(value: str) -> str:
    if not value:
        return value
    path = PureWindowsPath(value)
    if path.is_absolute() or path.drive or '..' in path.parts:
        raise ValueError(f'Expected relative path: {value!r}')
    def clean(part):
        # ESE preserves the digit in circled 9 and normalizes leftover spaces.
        return ' '.join(re.sub(r'[^A-Za-z0-9 ]', '', part.replace('\u2468', '9')).split())
    parts = [clean(part) for part in path.parts[:-1]]
    parts.append(clean(path.stem) + path.suffix)
    if any(not part for part in parts):
        raise ValueError(f'Empty component: {value!r}')
    return '\\'.join(parts)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ese-root', type=Path, default=Path(__file__).resolve().parent.parent / 'ESE')
    parser.add_argument('--write', action='store_true', help='Save changes; default is dry run')
    args = parser.parse_args()
    if not args.ese_root.is_dir():
        parser.error(f'ESE directory does not exist: {args.ese_root}')
    data = load_data()
    updated = {key: clean_path(value) for key, value in data.items()}
    missing = [(key, value) for key, value in updated.items() if value and not args.ese_root.joinpath(*PureWindowsPath(value).parts).is_file()]
    for key, value in missing:
        print(f'Missing [{key}]: {value}')
    print(f'{sum(data[key] != value for key, value in updated.items())} changed paths; {len(missing)} missing targets.')
    if missing:
        return 1
    if args.write:
        save_data(updated)
        print('Saved data.json.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
