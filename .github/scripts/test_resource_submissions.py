#!/usr/bin/env python3
"""Unit tests for resource_submissions.py runtime-optimization changes.

Run:  python3 -m unittest discover -s .github/scripts -v
Only the standard library is used; every network call is mocked.
"""

from __future__ import annotations

import email.message
import importlib.util
import io
import json
import os
import sys
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest import mock

SCRIPT_PATH = Path(__file__).resolve().parent / "resource_submissions.py"
SPEC = importlib.util.spec_from_file_location("resource_submissions", SCRIPT_PATH)
rs = importlib.util.module_from_spec(SPEC)
sys.modules["resource_submissions"] = rs
SPEC.loader.exec_module(rs)

VALID_ROW = "demo-id,Demo,quick_app,owner,repo,abcdef1,i.png,c.png,t,v,d,"


def write_catalog(directory: Path, row_count: int = 1) -> None:
    rows = [rs.HEADER_LINE] + [VALID_ROW for _ in range(row_count)]
    (directory / rs.CATALOG_PATH).write_text("\n".join(rows), newline="")


class FakeResponse:
    def __init__(self, body: bytes):
        self._body = body

    def read(self) -> bytes:
        return self._body

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, *args: object) -> bool:
        return False


def http_error(code: int, headers: dict[str, str] | None = None) -> urllib.error.HTTPError:
    message = email.message.Message()
    for key, value in (headers or {}).items():
        message[key] = value
    return urllib.error.HTTPError(
        url="https://api.github.com/x",
        code=code,
        msg="err",
        hdrs=message,
        fp=io.BytesIO(b'{"message":"err"}'),
    )


class ApiRetryTests(unittest.TestCase):
    def setUp(self) -> None:
        rs.API_STATS.update(rest=0, graphql=0)
        env = mock.patch.dict(
            os.environ, {"GITHUB_TOKEN": "t", "GITHUB_REPOSITORY": "o/r"}
        )
        env.start()
        self.addCleanup(env.stop)

    def test_get_retries_on_5xx_then_succeeds(self) -> None:
        responses = [http_error(502), http_error(503), FakeResponse(b'{"ok":true}')]
        with mock.patch.object(rs.time, "sleep") as sleeper, mock.patch(
            "urllib.request.urlopen", side_effect=responses
        ) as urlopen:
            data = rs.api_request("GET", "/repos/o/r/x")
        self.assertEqual(data, {"ok": True})
        self.assertEqual(urlopen.call_count, 3)
        self.assertEqual(sleeper.call_count, 2)

    def test_4xx_is_not_retried(self) -> None:
        with mock.patch.object(rs.time, "sleep") as sleeper, mock.patch(
            "urllib.request.urlopen", side_effect=http_error(404)
        ) as urlopen:
            with self.assertRaises(rs.SubmissionError):
                rs.api_request("GET", "/repos/o/r/x")
        self.assertEqual(urlopen.call_count, 1)
        self.assertEqual(sleeper.call_count, 0)

    def test_post_is_never_retried(self) -> None:
        with mock.patch.object(rs.time, "sleep"), mock.patch(
            "urllib.request.urlopen", side_effect=http_error(502)
        ) as urlopen:
            with self.assertRaises(rs.SubmissionError):
                rs.api_request("POST", "/repos/o/r/x", body={})
        self.assertEqual(urlopen.call_count, 1)

    def test_urlerror_is_retried(self) -> None:
        with mock.patch.object(rs.time, "sleep"), mock.patch(
            "urllib.request.urlopen",
            side_effect=[urllib.error.URLError("boom"), FakeResponse(b"{}")],
        ) as urlopen:
            self.assertEqual(rs.api_request("GET", "/x"), {})
        self.assertEqual(urlopen.call_count, 2)

    def test_retry_after_header_is_honored(self) -> None:
        with mock.patch.object(rs.time, "sleep") as sleeper, mock.patch(
            "urllib.request.urlopen",
            side_effect=[http_error(503, {"Retry-After": "7"}), FakeResponse(b"{}")],
        ):
            rs.api_request("GET", "/x")
        delay = sleeper.call_args[0][0]
        self.assertGreaterEqual(delay, 7.0)

    def test_retry_delay_caps_retry_after(self) -> None:
        self.assertGreaterEqual(rs.retry_delay(0, "999"), 15.0)
        self.assertLess(rs.retry_delay(0, None), 1.6)


class GraphqlRequestTests(unittest.TestCase):
    def setUp(self) -> None:
        rs.API_STATS.update(rest=0, graphql=0)
        env = mock.patch.dict(
            os.environ, {"GITHUB_TOKEN": "t", "GITHUB_REPOSITORY": "o/r"}
        )
        env.start()
        self.addCleanup(env.stop)

    def test_errors_array_is_fatal(self) -> None:
        body = json.dumps({"errors": [{"message": "boom"}]}).encode()
        with mock.patch("urllib.request.urlopen", return_value=FakeResponse(body)):
            with self.assertRaisesRegex(rs.SubmissionError, "boom"):
                rs.graphql_request("query {}")

    def test_missing_data_is_fatal(self) -> None:
        with mock.patch(
            "urllib.request.urlopen", return_value=FakeResponse(b'{"data": null}')
        ):
            with self.assertRaises(rs.SubmissionError):
                rs.graphql_request("query {}")

    def test_success_returns_data(self) -> None:
        body = json.dumps({"data": {"repository": {"x": 1}}}).encode()
        with mock.patch("urllib.request.urlopen", return_value=FakeResponse(body)):
            self.assertEqual(rs.graphql_request("q"), {"repository": {"x": 1}})


class ParseEventTests(unittest.TestCase):
    @staticmethod
    def write_event(payload: dict) -> str:
        file = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
        json.dump(payload, file)
        file.close()
        return file.name

    def setUp(self) -> None:
        self._files: list[str] = []

    def tearDown(self) -> None:
        for name in self._files:
            Path(name).unlink(missing_ok=True)

    def event(self, payload: dict) -> str:
        name = self.write_event(payload)
        self._files.append(name)
        return name

    def test_single_merge_in_head_commit(self) -> None:
        event = self.event(
            {"head_commit": {"message": "Merge pull request #669 from a/b"}}
        )
        self.assertEqual(rs.parse_pr_numbers_from_event(event), [669])

    def test_multiple_commits_dedup_preserving_order(self) -> None:
        event = self.event(
            {
                "head_commit": {"message": "Merge pull request #48 from a/b"},
                "commits": [
                    {"message": "Merge pull request #47 from c/d"},
                    {"message": "Merge pull request #47 from c/d"},
                ],
            }
        )
        self.assertEqual(rs.parse_pr_numbers_from_event(event), [48, 47])

    def test_squash_message_yields_nothing(self) -> None:
        event = self.event(
            {"head_commit": {"message": "[ABCC] Update resource: X (#123)"}}
        )
        self.assertEqual(rs.parse_pr_numbers_from_event(event), [])

    def test_missing_env_var_is_not_an_error(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("GITHUB_EVENT_PATH", None)
            self.assertEqual(rs.parse_pr_numbers_from_event(), [])

    def test_nonexistent_path_is_not_an_error(self) -> None:
        self.assertEqual(rs.parse_pr_numbers_from_event("/nonexistent/path.json"), [])


class MappingTests(unittest.TestCase):
    def setUp(self) -> None:
        rs.API_STATS.update(rest=0, graphql=0)

    @staticmethod
    def info(number: int, updated_at: str) -> dict:
        return {
            "number": number,
            "merged_at": "2026-08-20T00:00:00Z",
            "updated_at": updated_at,
            "merge_commit_sha": f"sha-{number}",
        }

    def test_first_wins_prefers_recently_updated_pr(self) -> None:
        mapping = rs._PrMapping()
        mapping.add(10, self.info(10, "2026-08-01T00:00:00Z"), ["tmp/a/repo"])
        mapping.add(11, self.info(11, "2026-08-02T00:00:00Z"), ["tmp/a/repo"])
        self.assertEqual(mapping.path_to_pr["tmp/a/repo"], 11)
        self.assertEqual(mapping.merged_at_map()[11], "2026-08-20T00:00:00Z")

    def test_fast_path_hit_skips_graphql(self) -> None:
        with mock.patch.object(
            rs, "parse_pr_numbers_from_event", return_value=[10]
        ), mock.patch.object(
            rs, "pull_info", side_effect=lambda n: self.info(n, "2026-08-01T00:00:00Z")
        ), mock.patch.object(
            rs,
            "pull_files",
            return_value=[{"filename": "tmp/a/repo/resource.csv"}],
        ), mock.patch.object(
            rs, "graphql_request", side_effect=AssertionError("must not be called")
        ):
            path_to_pr, merged_at, infos = rs.map_submission_paths_to_prs(
                {"tmp/a/repo"}
            )
        self.assertEqual(path_to_pr, {"tmp/a/repo": 10})
        self.assertIn(10, merged_at)
        # Fast-path cache carries merge_commit_sha so apply loop reuses it.
        self.assertEqual(infos[10]["merge_commit_sha"], "sha-10")

    def test_unmerged_event_pr_dropped_and_fallback_fills(self) -> None:
        def fake_graphql(query: str, variables: dict | None = None) -> dict:
            return {
                "repository": {
                    "pullRequests": {
                        "nodes": [
                            {
                                "number": 20,
                                "mergedAt": "2026-08-19T00:00:00Z",
                                "updatedAt": "2026-08-19T00:00:00Z",
                                "files": {
                                    "nodes": [{"path": "tmp/a/repo/resource.csv"}]
                                },
                            },
                            {
                                "number": 21,
                                "mergedAt": None,
                                "updatedAt": "2026-08-20T00:00:00Z",
                                "files": {
                                    "nodes": [{"path": "tmp/other/x/resource.csv"}]
                                },
                            },
                        ]
                    }
                }
            }

        with mock.patch.object(
            rs, "parse_pr_numbers_from_event", return_value=[]
        ), mock.patch.object(rs, "graphql_request", side_effect=fake_graphql):
            path_to_pr, merged_at, infos = rs.map_submission_paths_to_prs(
                {"tmp/a/repo"}
            )
        self.assertEqual(path_to_pr, {"tmp/a/repo": 20})
        self.assertIn(20, merged_at)
        self.assertNotIn(21, infos)
        # GraphQL-only info has no merge_commit_sha; apply loop must re-fetch.
        self.assertIsNone(infos[20]["merge_commit_sha"])

    def test_fallback_does_not_clobber_fast_path_cache(self) -> None:
        def fake_graphql(query: str, variables: dict | None = None) -> dict:
            return {
                "repository": {
                    "pullRequests": {
                        "nodes": [
                            {
                                "number": 10,
                                "mergedAt": "2026-08-18T00:00:00Z",
                                "updatedAt": "2026-08-01T00:00:00Z",
                                "files": {
                                    "nodes": [{"path": "tmp/a/repo/missed.csv"}]
                                },
                            }
                        ]
                    }
                }
            }

        with mock.patch.object(
            rs, "parse_pr_numbers_from_event", return_value=[10]
        ), mock.patch.object(
            rs, "pull_info", side_effect=lambda n: self.info(n, "2026-08-01T00:00:00Z")
        ), mock.patch.object(
            rs,
            "pull_files",
            return_value=[
                {"filename": "tmp/a/repo/resource.csv"},
                {"filename": "other/file.txt"},
            ],
        ), mock.patch.object(
            rs, "graphql_request", side_effect=fake_graphql
        ):
            path_to_pr, _, infos = rs.map_submission_paths_to_prs(
                {"tmp/a/repo"}
            )
        self.assertEqual(path_to_pr["tmp/a/repo"], 10)
        # Full REST info must survive the fallback pass.
        self.assertEqual(infos[10]["merge_commit_sha"], "sha-10")

    def test_graphql_failure_is_fatal(self) -> None:
        with mock.patch.object(
            rs, "parse_pr_numbers_from_event", return_value=[]
        ), mock.patch.object(
            rs,
            "graphql_request",
            side_effect=rs.SubmissionError("GitHub GraphQL 查询错误：boom"),
        ):
            with self.assertRaisesRegex(rs.SubmissionError, "GraphQL"):
                rs.map_submission_paths_to_prs({"tmp/a/repo"})


class EarlyExitTests(unittest.TestCase):
    def setUp(self) -> None:
        rs.API_STATS.update(rest=0, graphql=0)

    @staticmethod
    def run_apply() -> tuple[int, str]:
        buffer = io.StringIO()
        with mock.patch.dict(
            os.environ, {"GITHUB_TOKEN": "t", "GITHUB_REPOSITORY": "o/r"}
        ), mock.patch(
            "urllib.request.urlopen",
            side_effect=AssertionError("no API calls expected"),
        ), mock.patch.object(sys, "stdout", buffer):
            code = rs.command_apply_pending()
        return code, buffer.getvalue()

    def test_empty_tmp_exits_zero_without_api_calls(self) -> None:
        original_cwd = os.getcwd()
        with tempfile.TemporaryDirectory() as workdir:
            os.chdir(workdir)
            try:
                write_catalog(Path(workdir))
                code, output = self.run_apply()
            finally:
                os.chdir(original_cwd)
        self.assertEqual(code, 0)
        self.assertIn("无待处理提交", output)
        self.assertEqual(rs.API_STATS["rest"], 0)
        self.assertEqual(rs.API_STATS["graphql"], 0)

    def test_broken_index_fails_before_any_api_call(self) -> None:
        original_cwd = os.getcwd()
        with tempfile.TemporaryDirectory() as workdir:
            os.chdir(workdir)
            try:
                (Path(workdir) / rs.CATALOG_PATH).write_text(
                    f"{rs.HEADER_LINE}\n{VALID_ROW},extra\n", newline=""
                )
                code, output = self.run_apply()
            finally:
                os.chdir(original_cwd)
        self.assertEqual(code, 1)
        self.assertIn("列数不正确", output)
        self.assertEqual(rs.API_STATS["rest"], 0)
        self.assertEqual(rs.API_STATS["graphql"], 0)


if __name__ == "__main__":
    unittest.main()
