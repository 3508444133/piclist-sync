# piclist-sync

一个用于图床记录同步的轻量工具。

## 用法

```bash
python piclist_sync.py --source source.json --target target.json
```

参数说明：

- `--source`：源图床记录 JSON 文件
- `--target`：目标图床记录 JSON 文件（不存在会自动创建）
- `--dry-run`：只预览同步结果，不落盘
- `--update-existing`：当记录键相同时，用 source 覆盖 target 中已有记录

## 支持的数据格式

支持以下两种 JSON 结构：

1. 直接是数组：`[{...}, {...}]`
2. 对象中包含 `images` 数组：`{"images": [{...}]}`