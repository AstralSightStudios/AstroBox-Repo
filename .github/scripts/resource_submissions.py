#!/usr/bin/env python3
"""AstroBox v2 resource submission CLI.

Commands:
  validate-index   Strictly validate index_v2.csv.
  validate-pr      Validate one PR containing tmp staging files.
  apply-pending    Apply merged pending submissions to index_v2.csv.

The script uses only the standard library and the GitHub REST API through
urllib.request. It intentionally does not run any code from contributor PRs.
"""

from __future__ import annotations

import base64
import csv
import hashlib
import io
import json
import os
import random
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


CATALOG_PATH = "index_v2.csv"
SUBMISSION_ROOT = "tmp"
SUBMISSION_CSV_FILE = "resource.csv"
SUBMISSION_REQUEST_FILE = "request.json"
HEADER = [
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
HEADER_LINE = ",".join(HEADER)
INVISIBLE_CHARACTERS = {
    "\u200b": "ZERO WIDTH SPACE",
    "\u200c": "ZERO WIDTH NON-JOINER",
    "\u200d": "ZERO WIDTH JOINER",
    "\u2060": "WORD JOINER",
    "\ufeff": "ZERO WIDTH NO-BREAK SPACE",
}
PATH_SEGMENT_RE = re.compile(r"^[a-z0-9](?:[a-z0-9._-]*[a-z0-9])?$")
API_BASE = "https://api.github.com"
GRAPHQL_URL = f"{API_BASE}/graphql"
MERGE_PR_MESSAGE_RE = re.compile(r"Merge pull request #(\d+)")
RETRY_BACKOFF_SECONDS = (1.0, 2.0, 4.0)
RETRY_CAP_SECONDS = 15.0
API_STATS = {"rest": 0, "graphql": 0}


def apply_log(message: str) -> None:
    print(f"[apply-pending] {message}")


def retry_delay(attempt_index: int, retry_after: str | None) -> float:
    delay = RETRY_BACKOFF_SECONDS[min(attempt_index, len(RETRY_BACKOFF_SECONDS) - 1)]
    if retry_after:
        try:
            delay = max(delay, min(float(retry_after), RETRY_CAP_SECONDS))
        except ValueError:
            pass
    return min(delay + random.uniform(0, 0.5), RETRY_CAP_SECONDS)


class SubmissionError(RuntimeError):
    """A hard validation/application error that should be surfaced."""


@dataclass
class Entry:
    values: dict[str, str]
    line_number: int | None = None

    def get(self, key: str) -> str:
        return self.values.get(key, "").strip()


@dataclass
class Request:
    mode: str
    original_id: str | None
    base_entry_digest: str | None
    base_catalog_commit: str | None


def annotation(message: str, file: str = CATALOG_PATH, line: int | None = None) -> None:
    message = message.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
    location = f"file={file}"
    if line is not None:
        location += f",line={line}"
    print(f"::error {location}::{message}")


def github_token() -> str:
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        raise SubmissionError("缺少 GITHUB_TOKEN。")
    return token


def github_repo() -> str:
    return os.environ.get("GITHUB_REPOSITORY", "AstralSightStudios/ABRepo-TestEnv")


def api_request(method: str, path: str, body: Any | None = None) -> Any:
    url = f"{API_BASE}{path}"
    data = None
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {github_token()}",
        "User-Agent": "astrobox-resource-submissions",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    # Only idempotent GETs are retried; every write in this script goes
    # through git push, so POST/PUT would have nothing to retry anyway.
    attempts = 3 if method.upper() == "GET" else 1
    last_error: SubmissionError | None = None
    for attempt in range(attempts):
        request = urllib.request.Request(url, data=data, headers=headers, method=method)
        API_STATS["rest"] += 1
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                raw = response.read()
                if not raw:
                    return None
                return json.loads(raw)
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            last_error = SubmissionError(
                f"GitHub API {exc.code} {path}: {detail[:300]}"
            )
            last_error.__cause__ = exc
            retry_after = exc.headers.get("Retry-After") if exc.headers else None
            if (
                method.upper() != "GET"
                or exc.code < 500
                or attempt == attempts - 1
            ):
                raise last_error
            time.sleep(retry_delay(attempt, retry_after))
        except (urllib.error.URLError, TimeoutError) as exc:
            last_error = SubmissionError(f"GitHub API 网络错误 {path}: {exc}")
            last_error.__cause__ = exc
            if method.upper() != "GET" or attempt == attempts - 1:
                raise last_error
            time.sleep(retry_delay(attempt, None))
    raise last_error  # pragma: no cover - defensive


def graphql_request(query: str, variables: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = json.dumps({"query": query, "variables": variables or {}}).encode("utf-8")
    request = urllib.request.Request(
        GRAPHQL_URL,
        data=payload,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {github_token()}",
            "User-Agent": "astrobox-resource-submissions",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    API_STATS["graphql"] += 1
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            data = json.loads(response.read())
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise SubmissionError(f"GitHub GraphQL HTTP {exc.code}：{detail[:300]}") from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        raise SubmissionError(f"GitHub GraphQL 网络错误：{exc}") from exc
    errors = data.get("errors")
    if errors:
        summary = "; ".join(str(item.get("message", item))[:200] for item in errors[:3])
        raise SubmissionError(f"GitHub GraphQL 查询错误：{summary}")
    result = data.get("data")
    if not isinstance(result, dict):
        raise SubmissionError("GitHub GraphQL 响应缺少 data。")
    return result


def read_text(path: str | Path) -> str:
    raw = Path(path).read_bytes()
    return raw.decode("utf-8-sig")


def read_remote_text(path: str, ref: str) -> str:
    safe_path = urllib.parse.quote(path, safe="")
    safe_ref = urllib.parse.quote(ref, safe="")
    data = api_request(
        "GET",
        f"/repos/{github_repo()}/contents/{safe_path}?ref={safe_ref}",
    )
    content = data.get("content", "")
    if data.get("encoding", "base64") != "base64":
        raise SubmissionError("不支持的非 base64 文件内容。")
    return base64.b64decode(content).decode("utf-8-sig")


def write_text(path: str | Path, content: str) -> None:
    Path(path).write_text(content, encoding="utf-8", newline="\n")


def safe_path_segment(value: str, label: str) -> str:
    normalized = value.strip().lower()
    if not normalized:
        raise SubmissionError(f"{label} 不能为空。")
    if any(character in normalized for character in INVISIBLE_CHARACTERS):
        raise SubmissionError(f"{label} 包含不可见字符。")
    if normalized in {".", ".."} or "/" in normalized or "\\" in normalized:
        raise SubmissionError(f"{label} 包含非法路径片段。")
    if not PATH_SEGMENT_RE.match(normalized):
        raise SubmissionError(f"{label} 只允许小写字母、数字、点、连字符和下划线。")
    return normalized


def parse_csv_rows(text: str, path: str) -> tuple[list[Entry], str]:
    try:
        lines = text.splitlines()
    except UnicodeDecodeError as exc:
        raise SubmissionError(f"{path} 不是有效 UTF-8：{exc}") from exc

    reader = csv.reader(io.StringIO(text), strict=True)
    try:
        header = next(reader)
    except StopIteration as exc:
        raise SubmissionError(f"{path} 为空。") from exc
    if header != HEADER:
        raise SubmissionError(
            f"{path} 表头不正确；应为：{HEADER_LINE}"
        )

    rows: list[Entry] = []
    for line_number, row in enumerate(reader, 2):
        if not row:
            continue
        if len(row) != len(HEADER):
            raise SubmissionError(
                f"{path} 第 {line_number} 行列数不正确：应有 {len(HEADER)} 列，实际 {len(row)} 列"
            )
        for index, value in enumerate(row):
            for char, name in INVISIBLE_CHARACTERS.items():
                if char in value:
                    raise SubmissionError(
                        f"{path} 第 {line_number} 行第 {index + 1} 列包含零宽字符 U+{ord(char):04X} ({name})"
                    )
            if "\ufffd" in value:
                raise SubmissionError(f"{path} 第 {line_number} 行包含乱码替换字符 U+FFFD")
        rows.append(
            Entry(dict(zip(HEADER, row)), line_number=line_number)
        )
    return rows, lines[0] if lines else ""


def validate_devices_format(entry: Entry) -> None:
    devices = entry.get("devices")
    if "," in devices or '"' in devices:
        raise SubmissionError(
            f"资源 {entry.get('id') or 'unknown'} 的 devices 列格式不统一："
            "请用分号分隔设备，不要包含逗号或双引号。"
        )


def validate_index_entries(entries: list[Entry]) -> None:
    ids: dict[str, list[Entry]] = {}
    repos: dict[tuple[str, str], list[Entry]] = {}
    for entry in entries:
        id_value = entry.get("id")
        repo_key = (entry.get("repo_owner").lower(), entry.get("repo_name").lower())
        if not id_value:
            raise SubmissionError("目录中存在空资源 ID。")
        validate_devices_format(entry)
        ids.setdefault(id_value.lower(), []).append(entry)
        if all(repo_key):
            repos.setdefault(repo_key, []).append(entry)

    for key, duplicates in ids.items():
        if len(duplicates) > 1:
            lines = ", ".join(str(item.line_number) for item in duplicates)
            raise SubmissionError(f"资源 ID 重复：{key}；重复行：{lines}")
    for key, duplicates in repos.items():
        if len(duplicates) > 1:
            lines = ", ".join(str(item.line_number) for item in duplicates)
            raise SubmissionError(f"资源仓库重复：{key[0]}/{key[1]}；重复行：{lines}")


def canonical_digest(entry: Entry) -> str:
    row = ",".join(entry.values.get(column, "").strip() for column in HEADER)
    return hashlib.sha256(row.encode("utf-8")).hexdigest()


def parse_submission_csv(text: str, path: str) -> Entry:
    entries, _ = parse_csv_rows(text, path)
    if len(entries) != 1:
        raise SubmissionError(f"{path} 必须精确包含 1 行数据，当前为 {len(entries)} 行。")
    return entries[0]


def parse_request_json(text: str, path: str) -> Request:
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise SubmissionError(f"{path} 不是合法 JSON：{exc}") from exc
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise SubmissionError(f"{path} schema_version 必须为 1。")
    mode = data.get("mode")
    if mode not in {"create", "edit"}:
        raise SubmissionError(f"{path} mode 必须为 create 或 edit。")
    original_id = data.get("original_id")
    digest = data.get("base_entry_digest")
    commit = data.get("base_catalog_commit")
    if mode == "edit" and (not original_id or not digest or not commit):
        raise SubmissionError(
            f"{path} edit 请求必须提供 original_id、base_entry_digest、base_catalog_commit。"
        )
    return Request(
        mode=mode,
        original_id=str(original_id).strip() if original_id is not None else None,
        base_entry_digest=str(digest).strip() if digest is not None else None,
        base_catalog_commit=str(commit).strip() if commit is not None else None,
    )


def submission_dir_from_file(filename: str) -> str | None:
    parts = filename.split("/")
    if len(parts) < 4 or parts[0] != SUBMISSION_ROOT:
        return None
    return "/".join(parts[:3])


def list_submission_dirs() -> list[str]:
    root = Path(SUBMISSION_ROOT)
    if not root.exists():
        return []
    dirs: list[str] = []
    for request_path in sorted(root.rglob(SUBMISSION_REQUEST_FILE)):
        directory = request_path.parent
        relative = directory.relative_to(".").as_posix()
        dirs.append(relative)
    return dirs


def read_submission(directory: str) -> tuple[Entry, Request]:
    csv_path = Path(directory) / SUBMISSION_CSV_FILE
    request_path = Path(directory) / SUBMISSION_REQUEST_FILE
    entry = parse_submission_csv(read_text(csv_path), str(csv_path))
    request = parse_request_json(read_text(request_path), str(request_path))
    return entry, request


def find_entry(entries: list[Entry], resource_id: str) -> Entry | None:
    needle = resource_id.strip().lower()
    for entry in entries:
        if entry.get("id").lower() == needle:
            return entry
    return None


def find_entry_index(entries: list[Entry], resource_id: str) -> int | None:
    needle = resource_id.strip().lower()
    for index, entry in enumerate(entries):
        if entry.get("id").lower() == needle:
            return index
    return None


def validate_edit_or_create(
    entries: list[Entry],
    entry: Entry,
    request: Request,
) -> Entry | None:
    new_id = entry.get("id")
    if not new_id:
        raise SubmissionError("资源 ID 不能为空。")
    validate_devices_format(entry)
    if request.mode == "create":
        duplicate = find_entry(entries, new_id)
        if duplicate:
            raise SubmissionError(f"资源 ID {new_id} 已存在。")
        repo_duplicate = next(
            (
                item
                for item in entries
                if item.get("repo_owner").lower() == entry.get("repo_owner").lower()
                and item.get("repo_name").lower() == entry.get("repo_name").lower()
            ),
            None,
        )
        if repo_duplicate:
            raise SubmissionError(
                f"资源仓库 {entry.get('repo_owner')}/{entry.get('repo_name')} 已存在。"
            )
        return None

    original_id = request.original_id or ""
    original = find_entry(entries, original_id)
    if not original:
        raise SubmissionError(f"未找到原资源 ID {original_id}。")
    if canonical_digest(original) != request.base_entry_digest:
        raise SubmissionError(f"原资源 {original_id} 的目录行 digest 已过期。")
    if new_id.lower() != original_id.lower():
        duplicate = find_entry(entries, new_id)
        if duplicate:
            raise SubmissionError(f"新资源 ID {new_id} 已被其他资源占用。")
    return original


def normalize_repo_path(path: str) -> str:
    normalized = path.replace("\\", "/").strip()
    if not normalized or normalized.startswith("/") or ".." in normalized.split("/"):
        raise SubmissionError(f"包体路径非法：{path}")
    return normalized


def get_commit(owner: str, repo: str, ref: str) -> dict[str, Any]:
    safe_ref = urllib.parse.quote(ref, safe="")
    return api_request("GET", f"/repos/{owner}/{repo}/commits/{safe_ref}")


def get_tree_blobs(owner: str, repo: str, tree_sha: str) -> dict[str, dict[str, Any]]:
    data = api_request(
        "GET",
        f"/repos/{owner}/{repo}/git/trees/{tree_sha}?recursive=1",
    )
    if data.get("truncated"):
        raise SubmissionError(f"{owner}/{repo} 的 Git tree 被截断。")
    result: dict[str, dict[str, Any]] = {}
    for item in data.get("tree", []):
        if item.get("type") == "blob":
            result[item["path"]] = item
    return result


def get_blob_content(owner: str, repo: str, blob_sha: str) -> str:
    data = api_request("GET", f"/repos/{owner}/{repo}/git/blobs/{blob_sha}")
    content = data.get("content", "")
    encoding = data.get("encoding", "base64")
    if encoding != "base64":
        raise SubmissionError(f"不支持的 blob 编码：{encoding}")
    return base64.b64decode(content).decode("utf-8-sig")


def manifest_package_paths(manifest: dict[str, Any]) -> list[str]:
    paths: list[str] = []
    downloads = manifest.get("downloads") or {}
    if isinstance(downloads, dict):
        for info in downloads.values():
            if isinstance(info, dict) and info.get("file_name"):
                paths.append(str(info["file_name"]))
    ext = manifest.get("ext") or {}
    trial = ext.get("trialDownloads") if isinstance(ext, dict) else None
    if isinstance(trial, dict):
        for info in trial.values():
            if isinstance(info, dict) and info.get("file_name"):
                paths.append(str(info["file_name"]))
    return [normalize_repo_path(path) for path in paths]


def package_blob_set(owner: str, repo: str, commit_sha: str) -> frozenset[str]:
    commit = get_commit(owner, repo, commit_sha)
    tree_sha = commit.get("commit", {}).get("tree", {}).get("sha")
    if not tree_sha:
        raise SubmissionError(f"无法读取 {owner}/{repo}@{commit_sha} 的 tree。")
    blobs = get_tree_blobs(owner, repo, tree_sha)
    manifest_blob = blobs.get("manifest_v2.json") or blobs.get("manifest.json")
    if not manifest_blob:
        raise SubmissionError(f"{owner}/{repo}@{commit_sha} 缺少 manifest_v2.json。")
    manifest_text = get_blob_content(owner, repo, manifest_blob["sha"])
    try:
        manifest = json.loads(manifest_text)
    except json.JSONDecodeError as exc:
        raise SubmissionError(f"manifest_v2.json 解析失败：{exc}") from exc

    result: set[str] = set()
    for path in manifest_package_paths(manifest):
        blob = blobs.get(path)
        if not blob:
            raise SubmissionError(f"manifest 引用的包体不存在：{path}")
        result.add(blob["sha"])
    return frozenset(result)


PULL_REQUEST_WINDOW_QUERY = """
query($owner: String!, $name: String!) {
  repository(owner: $owner, name: $name) {
    pullRequests(states: MERGED, orderBy: {field: UPDATED_AT, direction: DESC}, first: 100) {
      nodes {
        number
        title
        mergedAt
        updatedAt
        files(first: 100) { nodes { path } }
      }
    }
  }
}
"""


def parse_pr_numbers_from_event(event_path: str | None = None) -> list[int]:
    """Extract candidate merged-PR numbers from the push event payload."""
    path = event_path or os.environ.get("GITHUB_EVENT_PATH", "")
    if not path or not Path(path).is_file():
        apply_log("未找到 GITHUB_EVENT_PATH，跳过快路径。")
        return []
    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        apply_log(f"事件 payload 读取失败，跳过快路径：{exc}")
        return []
    messages: list[str] = []
    head = payload.get("head_commit") if isinstance(payload, dict) else None
    if isinstance(head, dict) and head.get("message"):
        messages.append(str(head["message"]))
    commits = payload.get("commits") if isinstance(payload, dict) else None
    if isinstance(commits, list):
        for commit in commits:
            if isinstance(commit, dict) and commit.get("message"):
                messages.append(str(commit["message"]))
    numbers: list[int] = []
    for message in messages:
        match = MERGE_PR_MESSAGE_RE.search(message)
        if match:
            number = int(match.group(1))
            if number not in numbers:
                numbers.append(number)
    return numbers


def pull_files(pr_number: int) -> list[dict[str, Any]]:
    return api_request("GET", f"/repos/{github_repo()}/pulls/{pr_number}/files?per_page=100")


def pull_info(pr_number: int) -> dict[str, Any]:
    return api_request("GET", f"/repos/{github_repo()}/pulls/{pr_number}")


def _submission_dirs_from_files(files: list[dict[str, Any]], key: str) -> list[str]:
    directories = []
    for file in files:
        directory = submission_dir_from_file((file.get(key) or "") if isinstance(file, dict) else "")
        if directory and directory not in directories:
            directories.append(directory)
    return directories


class _PrMapping:
    """dir -> owning merged PR, preferring the most recently updated PR."""

    def __init__(self) -> None:
        self.path_to_pr: dict[str, int] = {}
        self.infos: dict[int, dict[str, Any]] = {}

    def add(self, number: int, info: dict[str, Any], directories: list[str]) -> None:
        self.infos[number] = info
        updated_at = str(info.get("updated_at") or "")
        for directory in directories:
            current = self.path_to_pr.get(directory)
            if current is None:
                self.path_to_pr[directory] = number
                continue
            current_updated = str(self.infos[current].get("updated_at") or "")
            if updated_at > current_updated:
                self.path_to_pr[directory] = number

    def merged_at_map(self) -> dict[int, str]:
        return {
            number: str(info["merged_at"])
            for number, info in self.infos.items()
            if info.get("merged_at")
        }


def map_submission_paths_to_prs(
    wanted_directories: set[str],
) -> tuple[dict[str, int], dict[int, str], dict[int, dict[str, Any]]]:
    """Map pending submission dirs to their owning merged PR.

    Fast path inspects only PRs referenced by the push event payload;
    a single GraphQL window scan fills in whatever is left (backlog,
    squash merges, workflow_dispatch). Returns (dir->PR, PR->merged_at,
    cached pull_info per PR).
    """
    mapping = _PrMapping()

    for number in parse_pr_numbers_from_event():
        info = pull_info(number)
        if not info.get("merged_at"):
            continue
        files = pull_files(number)
        mapping.add(number, info, _submission_dirs_from_files(files, "filename"))

    unmapped = {
        directory
        for directory in wanted_directories
        if directory not in mapping.path_to_pr
    }
    if not unmapped:
        return mapping.path_to_pr, mapping.merged_at_map(), mapping.infos

    owner, name = github_repo().split("/", 1)
    data = graphql_request(PULL_REQUEST_WINDOW_QUERY, {"owner": owner, "name": name})
    repository = data.get("repository") or {}
    nodes = ((repository.get("pullRequests") or {}).get("nodes")) or []
    for node in nodes:
        number = node.get("number")
        if not number or not node.get("mergedAt"):
            continue
        existing_info = mapping.infos.get(int(number))
        info = existing_info or {
            "number": number,
            "merged_at": node.get("mergedAt"),
            "updated_at": node.get("updatedAt"),
            "merge_commit_sha": None,
        }
        files = (node.get("files") or {}).get("nodes") or []
        directories = [
            directory
            for directory in _submission_dirs_from_files(files, "path")
            if directory in unmapped
        ]
        mapping.add(int(number), info, directories)

    return mapping.path_to_pr, mapping.merged_at_map(), mapping.infos


def commit_author(sha: str) -> tuple[str, str]:
    info = api_request("GET", f"/repos/{github_repo()}/git/commits/{sha}")
    author = info.get("author") or {}
    name = author.get("name") or "AstroBox Maintainer"
    email = author.get("email") or "maintainer@users.noreply.github.com"
    return str(name), str(email)


def creator_coauthor(pr_number: int) -> tuple[str, str] | None:
    commits = api_request("GET", f"/repos/{github_repo()}/pulls/{pr_number}/commits?per_page=100")
    if not commits:
        return None
    author = commits[-1].get("commit", {}).get("author") or {}
    name = author.get("name")
    email = author.get("email")
    if not name or not email:
        return None
    return str(name), str(email)


def run_git(args: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(
        ["git", *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if check and proc.returncode != 0:
        raise SubmissionError(f"git {' '.join(args)} 失败：{proc.stderr.strip()}")
    return proc


def prepare_apply_action(
    entries: list[Entry],
    entry: Entry,
    request: Request,
) -> dict[str, Any]:
    original = validate_edit_or_create(entries, entry, request)
    if request.mode == "create":
        existing = find_entry(entries, entry.get("id"))
        if existing and canonical_digest(existing) == canonical_digest(entry):
            return {"skip": True, "entry": entry, "request": request}
        if existing:
            raise SubmissionError(
                f"资源 ID {entry.get('id')} 已存在但内容不同，无法幂等新增。"
            )
        return {
            "skip": False,
            "entry": entry,
            "request": request,
            "original": None,
            "append": True,
        }

    assert original is not None
    if canonical_digest(original) == canonical_digest(entry):
        return {"skip": True, "entry": entry, "request": request, "original": original}

    old_blobs = package_blob_set(
        original.get("repo_owner"),
        original.get("repo_name"),
        original.get("repo_commit_hash"),
    )
    new_blobs = package_blob_set(
        entry.get("repo_owner"),
        entry.get("repo_name"),
        entry.get("repo_commit_hash"),
    )
    return {
        "skip": False,
        "entry": entry,
        "request": request,
        "original": original,
        "append": old_blobs != new_blobs,
    }


def entry_row(entry: Entry) -> str:
    output = io.StringIO()
    writer = csv.writer(output, lineterminator="")
    writer.writerow([entry.values.get(column, "").strip() for column in HEADER])
    return output.getvalue()


def write_index(entries: list[Entry]) -> None:
    content = "\n".join([HEADER_LINE, *[entry_row(entry) for entry in entries]]) + "\n"
    write_text(CATALOG_PATH, content)


def delete_submission_dir(directory: str) -> None:
    shutil.rmtree(directory, ignore_errors=True)


def commit_and_push(message: str, author_name: str, author_email: str, coauthor: tuple[str, str] | None) -> None:
    run_git(["add", "-A"])
    commit_args = ["-c", f"user.name={author_name}", "-c", f"user.email={author_email}", "commit", "-m", message]
    if coauthor:
        commit_args += ["-m", f"Co-authored-by: {coauthor[0]} <{coauthor[1]}>"]
    env = os.environ.copy()
    env["GIT_COMMITTER_NAME"] = "github-actions[bot]"
    env["GIT_COMMITTER_EMAIL"] = "41898282+github-actions[bot]@users.noreply.github.com"
    proc = subprocess.run(
        ["git", *commit_args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        env=env,
    )
    if proc.returncode != 0:
        raise SubmissionError(f"git commit 失败：{proc.stderr.strip()}")
    run_git(["push", "origin", "HEAD:main"])


def command_validate_index() -> int:
    try:
        text = read_text(CATALOG_PATH)
        entries, _ = parse_csv_rows(text, CATALOG_PATH)
        validate_index_entries(entries)
        print(f"检查完成：{len(entries)} 条数据，0 个错误")
        return 0
    except SubmissionError as exc:
        annotation(str(exc))
        return 1


def command_validate_pr() -> int:
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    if not event_path or not Path(event_path).exists():
        print("::warning::本地缺少 GITHUB_EVENT_PATH，跳过 PR 文件级校验。")
        return 0
    try:
        event = json.loads(Path(event_path).read_text(encoding="utf-8"))
        pr_number = event.get("number") or event.get("pull_request", {}).get("number")
        if not pr_number:
            raise SubmissionError("无法从 GitHub event 中读取 PR 编号。")
        files = pull_files(int(pr_number))
        dirs: set[str] = set()
        for file in files:
            filename = file.get("filename", "")
            if not filename.startswith(f"{SUBMISSION_ROOT}/"):
                raise SubmissionError(
                f"PR 不允许修改 {filename}；只允许修改 tmp/** 下的 resource.csv 和 request.json。"
                )
            if not filename.endswith(SUBMISSION_CSV_FILE) and not filename.endswith(
                SUBMISSION_REQUEST_FILE
            ):
                raise SubmissionError(f"PR 不允许修改 {filename}。")
            directory = submission_dir_from_file(filename)
            if directory:
                dirs.add(directory)
        if len(dirs) != 1:
            raise SubmissionError(
                f"每个 PR 只能包含一个 submission 目录，当前识别到 {len(dirs)} 个。"
            )

        base_sha = event.get("pull_request", {}).get("base", {}).get("sha")
        base_entries: list[Entry] = []
        if base_sha:
            base_entries, _ = parse_csv_rows(
                read_remote_text(CATALOG_PATH, base_sha),
                CATALOG_PATH,
            )

        for directory in dirs:
            entry, request = read_submission(directory)
            validate_edit_or_create(base_entries, entry, request)
            print(
                f"PR #{pr_number} 的 {directory} 通过本地结构校验："
                f"{request.mode} {entry.get('id')}"
            )
        return 0
    except SubmissionError as exc:
        annotation(str(exc))
        return 1


def command_apply_pending() -> int:
    started_at = time.monotonic()
    errors = 0
    applied = 0
    skipped = 0
    try:
        current_text = read_text(CATALOG_PATH)
        current_entries, _ = parse_csv_rows(current_text, CATALOG_PATH)
        validate_index_entries(current_entries)
    except SubmissionError as exc:
        annotation(str(exc))
        return 1

    submission_dirs = list_submission_dirs()
    apply_log(f"待处理目录：{len(submission_dirs)} 个")
    if not submission_dirs:
        apply_log("tmp/ 下无待处理提交，跳过扫描与应用。")
        _print_summary(started_at, applied, skipped, errors)
        return 0

    path_to_pr, merged_at, pr_infos = map_submission_paths_to_prs(set(submission_dirs))
    directories = [
        directory for directory in submission_dirs if directory in path_to_pr
    ]
    unmapped = [
        directory for directory in submission_dirs if directory not in path_to_pr
    ]
    if unmapped:
        apply_log(
            "警告：以下目录未找到对应的已合并 PR，保持原样：" + ", ".join(unmapped)
        )
    directories.sort(key=lambda directory: merged_at.get(path_to_pr[directory], ""))

    for directory in directories:
        pr_number = path_to_pr[directory]
        info = pr_infos.get(pr_number)
        if not isinstance(info, dict) or not info.get("merge_commit_sha"):
            info = pull_info(pr_number)
        merge_commit_sha = info.get("merge_commit_sha")
        if not merge_commit_sha:
            annotation(f"PR #{pr_number} 缺少 merge_commit_sha，无法确定维护者。")
            errors += 1
            continue
        try:
            entry, request = read_submission(directory)
            action = prepare_apply_action(current_entries, entry, request)
            if action.get("skip"):
                delete_submission_dir(directory)
                run_git(["add", "-A"])
                author_name, author_email = commit_author(merge_commit_sha)
                coauthor = creator_coauthor(pr_number)
                commit_and_push(
                    f"Apply resource submission from PR #{pr_number} ({directory})",
                    author_name,
                    author_email,
                    coauthor,
                )
                skipped += 1
                apply_log(
                    f"{directory}（PR #{pr_number}）：内容与当前目录一致，跳过并清理。"
                )
                continue

            if request.mode == "create":
                current_entries.append(entry)
            else:
                original = action["original"]
                original_index = find_entry_index(current_entries, original.get("id"))
                if original_index is None:
                    raise SubmissionError("原资源行已消失，无法应用更新。")
                if action["append"]:
                    current_entries.pop(original_index)
                    current_entries.append(entry)
                else:
                    current_entries[original_index] = entry

            write_index(current_entries)
            # Re-parse the serialized catalog so malformed rows (for example
            # unquoted commas) are caught before anything is pushed to main.
            current_entries, _ = parse_csv_rows(
                read_text(CATALOG_PATH), CATALOG_PATH
            )
            validate_index_entries(current_entries)
            delete_submission_dir(directory)
            author_name, author_email = commit_author(merge_commit_sha)
            coauthor = creator_coauthor(pr_number)
            commit_and_push(
                f"Apply resource submission from PR #{pr_number} ({directory})",
                author_name,
                author_email,
                coauthor,
            )
            applied += 1
            apply_log(
                f"{directory}（PR #{pr_number}）：已应用 {request.mode} "
                f"{entry.get('id')}，新 digest {canonical_digest(entry)[:12]}…"
            )
        except SubmissionError as exc:
            annotation(
                f"{directory}（PR #{pr_number}）应用失败：{exc}。"
                f"目标资源：{entry.get('id') if 'entry' in locals() else 'unknown'}",
                file=directory,
            )
            errors += 1
            continue

    _print_summary(started_at, applied, skipped, errors)
    return 1 if errors else 0


def _print_summary(started_at: float, applied: int, skipped: int, errors: int) -> None:
    elapsed = time.monotonic() - started_at
    apply_log(
        f"完成：应用 {applied} / 跳过 {skipped} / 失败 {errors}，"
        f"REST 调用 {API_STATS['rest']} 次、GraphQL {API_STATS['graphql']} 次，"
        f"耗时 {elapsed:.1f}s"
    )


def main() -> int:
    command = sys.argv[1] if len(sys.argv) > 1 else "validate-index"
    if command == "validate-index":
        return command_validate_index()
    if command == "validate-pr":
        return command_validate_pr()
    if command == "apply-pending":
        return command_apply_pending()
    print(f"未知命令：{command}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
