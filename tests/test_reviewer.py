import json
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from code_review_copilot.git_utils import truncate_diff
from code_review_copilot.reviewer import ReviewError, parse_review_response


class ParseReviewResponseTests(unittest.TestCase):
    def test_parses_valid_response(self):
        response = json.dumps(
            {
                "summary": "One issue found.",
                "findings": [
                    {
                        "severity": "high",
                        "file": "app.py",
                        "line": 12,
                        "title": "Secret committed",
                        "details": "Remove the credential.",
                    }
                ],
            }
        )

        result = parse_review_response(response)

        self.assertEqual(result.summary, "One issue found.")
        self.assertEqual(len(result.findings), 1)
        self.assertEqual(result.findings[0].severity, "high")
        self.assertEqual(result.findings[0].file, "app.py")

    def test_extracts_json_from_wrapped_model_text(self):
        response = 'Here is the review:\n{"summary": "OK", "findings": []}'

        result = parse_review_response(response)

        self.assertEqual(result.summary, "OK")
        self.assertEqual(result.findings, [])

    def test_rejects_missing_json(self):
        with self.assertRaises(ReviewError):
            parse_review_response("No structured output here.")


class TruncateDiffTests(unittest.TestCase):
    def test_leaves_short_diff_unchanged(self):
        diff, truncated = truncate_diff("abc", 10)

        self.assertEqual(diff, "abc")
        self.assertFalse(truncated)

    def test_truncates_long_diff(self):
        diff, truncated = truncate_diff("abcdef" * 30, 80)

        self.assertTrue(truncated)
        self.assertIn("truncated", diff)
        self.assertLessEqual(len(diff), 80)


if __name__ == "__main__":
    unittest.main()
