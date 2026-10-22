#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple


def _extract_images(payload: Any) -> Tuple[List[Dict[str, Any]], str]:
    if isinstance(payload, list):
        return payload, "list"
    if isinstance(payload, dict):
        images = payload.get("images")
        if isinstance(images, list):
            return images, "dict"
    raise ValueError("JSON must be a list or an object containing an 'images' list.")


def _item_key(item: Dict[str, Any]) -> str:
    if "id" in item and item["id"] not in (None, ""):
        return f"id:{item['id']}"
    if "url" in item and item["url"]:
        return f"url:{item['url']}"
    if "name" in item and item["name"]:
        return f"name:{item['name']}"
    return "raw:" + json.dumps(item, sort_keys=True, ensure_ascii=False)


def _load_json(path: Path) -> Any:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _dump_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def sync_records(
    source_path: Path,
    target_path: Path,
    *,
    dry_run: bool = False,
    update_existing: bool = False,
) -> Dict[str, int]:
    source_raw = _load_json(source_path)
    target_raw = _load_json(target_path)

    source_images, _ = _extract_images(source_raw)
    target_images, target_format = _extract_images(target_raw)

    target_index = {_item_key(item): idx for idx, item in enumerate(target_images)}

    added = 0
    updated = 0
    skipped = 0

    for source_item in source_images:
        key = _item_key(source_item)
        if key not in target_index:
            target_index[key] = len(target_images)
            target_images.append(source_item)
            added += 1
            continue

        existing_idx = target_index[key]
        if update_existing and target_images[existing_idx] != source_item:
            target_images[existing_idx] = source_item
            updated += 1
        else:
            skipped += 1

    if not dry_run:
        if target_format == "dict":
            target_raw["images"] = target_images
            output = target_raw
        else:
            output = target_images
        _dump_json(target_path, output)

    return {"added": added, "updated": updated, "skipped": skipped}


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync image-host records from source to target.")
    parser.add_argument("--source", required=True, help="Source JSON file path.")
    parser.add_argument("--target", required=True, help="Target JSON file path.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview sync result without writing changes.",
    )
    parser.add_argument(
        "--update-existing",
        action="store_true",
        help="Overwrite existing target records when key matches.",
    )
    args = parser.parse_args()

    result = sync_records(
        Path(args.source),
        Path(args.target),
        dry_run=args.dry_run,
        update_existing=args.update_existing,
    )
    print(
        f"Sync finished: added={result['added']}, "
        f"updated={result['updated']}, skipped={result['skipped']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
