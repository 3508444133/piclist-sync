import json
import tempfile
import unittest
from pathlib import Path

from piclist_sync import sync_records


class PicListSyncTests(unittest.TestCase):
    def test_adds_missing_records(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.json"
            target = root / "target.json"
            source.write_text(
                json.dumps(
                    [
                        {"url": "https://img.example/a.png", "name": "a"},
                        {"url": "https://img.example/b.png", "name": "b"},
                    ],
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            target.write_text(
                json.dumps([{"url": "https://img.example/a.png", "name": "a"}], ensure_ascii=False),
                encoding="utf-8",
            )

            result = sync_records(source, target)
            target_data = json.loads(target.read_text(encoding="utf-8"))

            self.assertEqual(result, {"added": 1, "updated": 0, "skipped": 1})
            self.assertEqual(len(target_data), 2)

    def test_dry_run_does_not_modify_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.json"
            target = root / "target.json"
            source.write_text(
                json.dumps([{"url": "https://img.example/a.png", "name": "a"}], ensure_ascii=False),
                encoding="utf-8",
            )
            target.write_text("[]", encoding="utf-8")

            result = sync_records(source, target, dry_run=True)

            self.assertEqual(result, {"added": 1, "updated": 0, "skipped": 0})
            self.assertEqual(target.read_text(encoding="utf-8"), "[]")

    def test_preserves_dict_format_with_images_key(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.json"
            target = root / "target.json"
            source.write_text(
                json.dumps({"images": [{"id": "1", "url": "https://img.example/new.png"}]}, ensure_ascii=False),
                encoding="utf-8",
            )
            target.write_text(
                json.dumps(
                    {"provider": "demo", "images": [{"id": "1", "url": "https://img.example/old.png"}]},
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            result = sync_records(source, target, update_existing=True)
            target_data = json.loads(target.read_text(encoding="utf-8"))

            self.assertEqual(result, {"added": 0, "updated": 1, "skipped": 0})
            self.assertEqual(target_data["provider"], "demo")
            self.assertEqual(target_data["images"][0]["url"], "https://img.example/new.png")


if __name__ == "__main__":
    unittest.main()
