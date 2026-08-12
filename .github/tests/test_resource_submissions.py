import unittest
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".github/scripts"))

import resource_submissions as rs


class SubmissionProtocolTests(unittest.TestCase):
    def test_parse_submission_csv_exact_two_rows(self):
        csv_text = (
            "id,name,restype,repo_owner,repo_name,repo_commit_hash,icon,cover,tags,device_vendors,devices,paid_type\n"
            "abc,资源,quick_app,owner,repo,abcdef0,icon.png,cover.png,tags,xiaomi,dev,\n"
        )
        entry = rs.parse_submission_csv(csv_text, "resource.csv")
        self.assertEqual(entry.get("id"), "abc")
        self.assertEqual(entry.get("repo_name"), "repo")

    def test_parse_submission_csv_rejects_extra_row(self):
        csv_text = (
            "id,name,restype,repo_owner,repo_name,repo_commit_hash,icon,cover,tags,device_vendors,devices,paid_type\n"
            "abc,资源,quick_app,owner,repo,abcdef0,icon.png,cover.png,tags,xiaomi,dev,\n"
            "abc2,资源2,quick_app,owner,repo,abcdef0,icon.png,cover.png,tags,xiaomi,dev,\n"
        )
        with self.assertRaises(rs.SubmissionError):
            rs.parse_submission_csv(csv_text, "resource.csv")

    def test_parse_request_json_edit_requires_digest(self):
        with self.assertRaises(rs.SubmissionError):
            rs.parse_request_json(
                '{"schema_version":1,"mode":"edit","original_id":"abc"}',
                "request.json",
            )

    def test_submission_dir_from_file(self):
        self.assertEqual(
            rs.submission_dir_from_file("tmp/alice/repo/request.json"),
            "tmp/alice/repo",
        )
        self.assertIsNone(rs.submission_dir_from_file("index_v2.csv"))

    def test_validate_duplicate_ids(self):
        rows = [
            {"id": "A", "name": "one"},
            {"id": "a", "name": "two"},
        ]
        entries = [
            rs.Entry({**dict.fromkeys(rs.HEADER, ""), **row})
            for row in rows
        ]
        with self.assertRaises(rs.SubmissionError):
            rs.validate_index_entries(entries)


if __name__ == "__main__":
    unittest.main()
