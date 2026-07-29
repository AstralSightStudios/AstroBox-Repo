#!/usr/bin/env python3
import csv
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import datetime


PATH = "index_v2.csv"
EXPECTED_COLUMNS = [
    "id",
    "name",
    "restype",
    "repo_owner",
    "repo_name",
    "repo_commit_hash",
    "icon",
    "cover",
    "tags",
    "device_vendors",
    "devices",
    "paid_type",
]
INVISIBLE_CHARACTERS = {
    "\u200b": "ZERO WIDTH SPACE",
    "\u200c": "ZERO WIDTH NON-JOINER",
    "\u200d": "ZERO WIDTH JOINER",
    "\u2060": "WORD JOINER",
    "\ufeff": "ZERO WIDTH NO-BREAK SPACE",
}


def annotation(message, line=None):
    message = message.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
    location = f"file={PATH},line={line}," if line else f"file={PATH},"
    print(f"::error {location}::{message}")


def commit_time(owner, repo, commit_hash):
    path = "/".join(urllib.parse.quote(part, safe="") for part in (owner, repo, "commits", commit_hash))
    request = urllib.request.Request(
        f"https://api.github.com/repos/{path}",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "index-v2-validator",
        },
    )
    with urllib.request.urlopen(request, timeout=15) as response:
        data = json.load(response)
    value = data["commit"]["committer"]["date"]
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def main():
    errors = 0
    try:
        raw = open(PATH, "rb").read()
        text = raw.decode("utf-8-sig")
    except (OSError, UnicodeDecodeError) as exc:
        annotation(f"文件不是有效 UTF-8：{exc}")
        return 1

    for line_number, line in enumerate(text.splitlines(), 1):
        for character, name in INVISIBLE_CHARACTERS.items():
            if character in line:
                annotation(f"发现零宽字符 U+{ord(character):04X} ({name})", line_number)
                errors += 1
        if "\ufffd" in line:
            annotation("发现乱码替换字符 U+FFFD", line_number)
            errors += 1

    rows = []
    try:
        reader = csv.reader(text.splitlines(keepends=True), strict=True)
        header = next(reader)
        if header != EXPECTED_COLUMNS:
            annotation(f"表头不正确；应为：{','.join(EXPECTED_COLUMNS)}", 1)
            errors += 1
        for row in reader:
            line_number = reader.line_num
            if len(row) != len(EXPECTED_COLUMNS):
                annotation(f"列数不正确：应有 {len(EXPECTED_COLUMNS)} 列，实际 {len(row)} 列", line_number)
                errors += 1
                continue
            rows.append((line_number, dict(zip(EXPECTED_COLUMNS, row))))
    except (csv.Error, StopIteration) as exc:
        annotation(f"CSV 格式错误：{exc}")
        return 1

    for columns in (("id",), ("repo_owner", "repo_name")):
        groups = defaultdict(list)
        for line_number, row in rows:
            key = tuple(row[column].strip().casefold() for column in columns)
            if all(key):
                groups[key].append((line_number, row))
        for key, duplicates in groups.items():
            if len(duplicates) < 2:
                continue
            label = "/".join(key)
            lines = ", ".join(str(line) for line, _ in duplicates)
            for line_number, _ in duplicates:
                annotation(f"{'+'.join(columns)} 重复：{label}；重复行：{lines}", line_number)
                errors += 1
            if columns == ("repo_owner", "repo_name"):
                dated = []
                for line_number, row in duplicates:
                    try:
                        dated.append((commit_time(row["repo_owner"], row["repo_name"], row["repo_commit_hash"]), line_number, row))
                    except (KeyError, ValueError, urllib.error.URLError, TimeoutError) as exc:
                        annotation(f"无法查询提交 {row['repo_commit_hash']} 的时间：{exc}", line_number)
                        errors += 1
                if dated:
                    commit_date, line_number, row = max(dated)
                    print(
                        f"重复仓库 {row['repo_owner']}/{row['repo_name']} 中最新提交："
                        f"第 {line_number} 行，hash {row['repo_commit_hash']}，时间 {commit_date.isoformat()}"
                    )

    print(f"检查完成：{len(rows)} 条数据，{errors} 个错误")
    return bool(errors)


if __name__ == "__main__":
    sys.exit(main())
