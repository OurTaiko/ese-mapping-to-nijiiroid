import json
import pprint
from typing import Any


class MappingItem:
    id: str
    esePath: str

    def __init__(self, id: str = "", esePath: str = ""):
        self.id = id
        self.esePath = esePath

    def __str__(self) -> str:
        return f"MappingItem(id={self.id}, esePath={self.esePath})"


def sort_key(item: MappingItem) -> tuple:
    """排序key：数字优先（按数值大小），然后字符串（按字母序）"""
    try:
        return (0, int(item.id))
    except ValueError:
        return (1, item.id)


def main():
    mapping_items: list[MappingItem] = []
    with open("song_mapping.json", "r", encoding="utf-8") as f:
        mapping: dict[str, dict[str, Any]] = json.load(f)
        for key, value in mapping.items():
            mapping_item = MappingItem(key, value["esePath"])
            mapping_items.append(mapping_item)

        mapping_items.sort(key=sort_key)

        with open("data.json", "w", encoding="utf-8") as f:
            json.dump(
                {item.id: item.esePath for item in mapping_items},
                f,
                indent=4,
            )


if __name__ == "__main__":
    main()
