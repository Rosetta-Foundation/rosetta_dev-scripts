from pathlib import Path
import importlib.util
import os
import unittest

HELPER = Path(__file__).resolve().parents[1] / "verify_slack.py"


def load_mod():
    spec = importlib.util.spec_from_file_location("verify_slack", HELPER)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


SAMPLE = """
## Verify on app.dev

### Not verified

**New this morning** (app.dev):

- [ ] Uploaded files show viewer-local date/time next to the
      filename.
- [ ] Case dialog: type `@` in Messages — picker + pills.

**New this morning** (admin.dev / console.dev):

- [ ] Awaiting-billing building stays in the picker on admin.dev.

### Verified

- [x] Already done item should not publish.
"""


class HostEnv:
    def __enter__(self):
        self._old = os.environ.get("VERIFY_SANDBOX_HOSTS")
        os.environ["VERIFY_SANDBOX_HOSTS"] = "app.dev,admin.dev,console.dev"
        return self

    def __exit__(self, *args):
        if self._old is None:
            os.environ.pop("VERIFY_SANDBOX_HOSTS", None)
        else:
            os.environ["VERIFY_SANDBOX_HOSTS"] = self._old


class ParseNotVerifiedTests(unittest.TestCase):
    def test_extracts_unchecked_lines_and_skips_verified(self):
        mod = load_mod()
        with HostEnv():
            rows = mod.parse_not_verified(SAMPLE)
        texts = [row["item"] for row in rows]
        self.assertEqual(len(rows), 3)
        self.assertIn("filename.", texts[0])
        self.assertEqual(rows[0]["host"], "app.dev")
        self.assertTrue(any("picker + pills" in t for t in texts))
        self.assertTrue(any(row["host"] == "admin.dev" for row in rows))
        self.assertFalse(any("Already done" in t for t in texts))


class SlackFieldShapeTests(unittest.TestCase):
    def test_item_status_reads_list_of_field_objects(self):
        mod = load_mod()
        entry = {
            "fields": [
                {
                    "column_id": "ColAAA",
                    "key": "name",
                    "text": "Mention emails fire",
                    "value": "Mention emails fire",
                },
                {
                    "column_id": "ColBBB",
                    "key": "Status",
                    "value": "Verified",
                    "select": "Verified",
                },
                {
                    "column_id": "ColCCC",
                    "key": "Notes",
                    "text": "ok on app.dev",
                    "value": "ok on app.dev",
                },
            ]
        }
        item, status, notes = mod.item_status(entry)
        self.assertEqual(item, "Mention emails fire")
        self.assertEqual(status, "verified")
        self.assertEqual(notes, "ok on app.dev")

    def test_item_fields_uses_column_id_and_typed_values(self):
        mod = load_mod()
        cols = {
            "item": "ColITEM",
            "host": "ColHOST",
            "status": "ColSTATUS",
            "ship": "ColSHIP",
        }
        fields = mod.item_fields(
            cols,
            item="Org switcher",
            host="app.dev",
            ship="123",
        )
        by_col = {field["column_id"]: field for field in fields}
        self.assertEqual(by_col["ColHOST"]["select"], ["app.dev"])
        self.assertEqual(by_col["ColSTATUS"]["select"], ["not_verified"])
        item_text = by_col["ColITEM"]["rich_text"][0]["elements"][0]["elements"][0][
            "text"
        ]
        self.assertEqual(item_text, "Org switcher")
        self.assertNotIn("key", fields[0])
        self.assertNotIn("value", fields[0])

    def test_parse_verify_heading_without_not_verified_section(self):
        mod = load_mod()
        markdown = """
## Verify on app.dev

- [ ] Org switcher on app.dev.
- [ ] Console hop.

## Out of this ship

- [ ] Should not publish.
"""
        with HostEnv():
            rows = mod.parse_not_verified(markdown)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["host"], "app.dev")
        self.assertFalse(any("Should not" in row["item"] for row in rows))


class SnapshotAndFailedTests(unittest.TestCase):
    def test_check_off_verified_flips_matching_checkbox(self):
        mod = load_mod()
        markdown = (
            "## Verify on app.dev\n\n"
            "- [ ] Org switcher on app.dev.\n"
            "- [ ] Console hop.\n\n"
            "## Out of this ship\n"
        )
        updated = mod.check_off_verified(
            markdown, {"Org switcher on app.dev."}
        )
        self.assertIn("- [x] Org switcher on app.dev.", updated)
        self.assertIn("- [ ] Console hop.", updated)

    def test_failed_comment_is_idempotent_by_marker(self):
        mod = load_mod()
        row = {
            "item": "Org switcher",
            "host": "app.dev",
            "ship": "123",
            "notes": "picker empty",
            "status": "failed",
        }
        body = mod.failed_comment_body(row)
        key = mod.failed_comment_key("123", "Org switcher")
        marker = mod.failed_marker(key)
        self.assertIn(marker, body)
        self.assertIn("picker empty", body)
        self.assertEqual(mod.ship_issue("#123 / 2026-08-13"), "123")


class ChannelNotifyTests(unittest.TestCase):
    def test_notice_includes_channel_mention_ship_and_list_url(self):
        mod = load_mod()
        text = mod.new_items_notice(
            ship="123",
            list_url="https://app.slack.com/lists/T0/F0",
            rows=[{"item": "Org switcher", "host": "app.dev"}],
        )
        self.assertIn("<!channel>", text)
        self.assertIn("Ship: #123", text)
        self.assertIn("[app.dev] Org switcher", text)
        self.assertIn("https://app.slack.com/lists/T0/F0", text)
        self.assertIn("1 new sandbox verify item to smoke", text)

    def test_notify_new_items_posts_configured_channel(self):
        mod = load_mod()
        calls: list[tuple[str, dict]] = []

        def fake_post(method, token, payload):
            calls.append((method, payload))
            return {"ok": True}

        orig = mod.slack_post
        mod.slack_post = fake_post
        try:
            mod.notify_new_items(
                "xoxb-test",
                channel="#verify-notify",
                list_url="https://app.slack.com/lists/T0/F0",
                ship="123",
                rows=[{"item": "Org switcher", "host": "app.dev"}],
            )
            mod.notify_new_items(
                "xoxb-test",
                channel="#verify-notify",
                list_url="https://app.slack.com/lists/T0/F0",
                ship="123",
                rows=[],
            )
        finally:
            mod.slack_post = orig
        self.assertEqual(len(calls), 1)
        method, payload = calls[0]
        self.assertEqual(method, "chat.postMessage")
        self.assertEqual(payload["channel"], "#verify-notify")
        self.assertIn("<!channel>", payload["text"])
        self.assertFalse(payload["unfurl_links"])

    def test_notify_channel_is_unset_by_default(self):
        mod = load_mod()
        old = os.environ.pop("VERIFY_NOTIFY_CHANNEL_ID", None)
        try:
            self.assertIsNone(mod.notify_channel())
            os.environ["VERIFY_NOTIFY_CHANNEL_ID"] = "C123"
            self.assertEqual(mod.notify_channel(), "C123")
        finally:
            if old is None:
                os.environ.pop("VERIFY_NOTIFY_CHANNEL_ID", None)
            else:
                os.environ["VERIFY_NOTIFY_CHANNEL_ID"] = old


if __name__ == "__main__":
    unittest.main()
