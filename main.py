import json
import sys
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


SONG_API_URL = "https://taiko.wiki/api/song"
DATA_FILE = Path(__file__).with_name("data.json")


def fetch_song_numbers(url: str = SONG_API_URL) -> set[str]:
    """从歌曲 API 获取所有 songNo，并统一转换为字符串。"""
    request = Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "ese-mapping-to-nijiiroid/1.0",
        },
    )
    with urlopen(request, timeout=30) as response:
        payload: Any = json.load(response)

    if not isinstance(payload, list):
        raise ValueError("API 返回的数据不是 JSON list")

    song_numbers: set[str] = set()
    for index, song in enumerate(payload):
        if not isinstance(song, dict):
            raise ValueError(f"API 第 {index} 项不是 JSON object")
        if "songNo" not in song:
            raise ValueError(f"API 第 {index} 项缺少 songNo")

        song_no = song["songNo"]
        if song_no is None or isinstance(song_no, (dict, list, bool)):
            raise ValueError(f"API 第 {index} 项的 songNo 无效: {song_no!r}")
        song_numbers.add(str(song_no))

    if not song_numbers:
        raise ValueError("API 没有返回任何 songNo，已取消同步以避免清空 data.json")

    return song_numbers


def load_data(path: Path = DATA_FILE) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        data: Any = json.load(file)

    if not isinstance(data, dict):
        raise ValueError(f"{path} 的顶层结构必须是 JSON object")
    return data


def song_number_sort_key(song_no: str) -> tuple[int, int | str, str]:
    """可解析为整数的编号优先按数值排序，其余编号按字符串排序。"""
    try:
        return (0, int(song_no), song_no)
    except ValueError:
        return (1, song_no, song_no)


def sync_data(
    data: dict[str, Any], song_numbers: set[str]
) -> tuple[dict[str, Any], list[str], list[str]]:
    current_keys = set(data)
    added = sorted(song_numbers - current_keys, key=song_number_sort_key)
    removed = sorted(current_keys - song_numbers, key=song_number_sort_key)

    synced = {
        song_no: data.get(song_no, "")
        for song_no in sorted(song_numbers, key=song_number_sort_key)
    }
    return synced, added, removed


def save_data(data: dict[str, Any], path: Path = DATA_FILE) -> None:
    temporary_path = path.with_suffix(f"{path.suffix}.tmp")
    with temporary_path.open("w", encoding="utf-8", newline="\n") as file:
        json.dump(data, file, ensure_ascii=True, indent=2)
        file.write("\n")
    temporary_path.replace(path)


def main() -> int:
    try:
        song_numbers = fetch_song_numbers()
        data = load_data()
        synced, added, removed = sync_data(data, song_numbers)
        save_data(synced)
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError, OSError, ValueError) as error:
        print(f"同步失败: {error}", file=sys.stderr)
        return 1

    print(
        f"同步完成：共 {len(synced)} 项，新增 {len(added)} 项，"
        f"删除 {len(removed)} 项。"
    )
    if added:
        print("新增:", ", ".join(added))
    if removed:
        print("删除:", ", ".join(removed))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
