import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from technocore_client import TechnocoreClient


class TestTechnocoreClient(unittest.TestCase):

    def setUp(self):
        self.client = TechnocoreClient()

    def test_did_fingerprint(self):
        did = (
            "did:key:z6MkgvPsAcVPX1JawE6DZRzKpoQLsZmu"
            "Azw8pnXsJfEKyVJ8"
        )

        fingerprint = self.client.did_fingerprint(did)

        self.assertEqual(
            fingerprint,
            "dc0504f2c9a43feb",
        )

    def test_did_note_path(self):
        did = (
            "did:key:z6MkgvPsAcVPX1JawE6DZRzKpoQLsZmu"
            "Azw8pnXsJfEKyVJ8"
        )

        path = self.client.did_note_path(did)

        self.assertEqual(
            path,
            "/kv/did-dc/0504f2c9a43feb",
        )

    def test_read_room_rejects_invalid_limit(self):
        with self.assertRaises(ValueError):
            self.client.read_room(
                "general",
                0,
            )

    @patch.object(
        TechnocoreClient,
        "read_room",
    )
    def test_history_export_deduplicates(
        self,
        mock_read_room,
    ):
        mock_read_room.return_value = (
            "# room general messages 2 range 1..2\n"
            "[100] 2026-09-05T00:00:00Z <z6Mk...> First message\n"
            "[101] 2026-09-05T00:01:00Z <z6Mk...> Second message\n"
        )

        with tempfile.TemporaryDirectory() as temp_dir:

            output_file = (
                Path(temp_dir)
                / "history.jsonl"
            )

            first_count = (
                self.client.save_room_history(
                    "general",
                    str(output_file),
                    20,
                )
            )

            second_count = (
                self.client.save_room_history(
                    "general",
                    str(output_file),
                    20,
                )
            )

            self.assertEqual(
                first_count,
                2,
            )

            self.assertEqual(
                second_count,
                0,
            )

            records = [
                json.loads(line)
                for line in output_file.read_text(
                    encoding="utf-8"
                ).splitlines()
            ]

            self.assertEqual(
                len(records),
                2,
            )

            self.assertEqual(
                records[0]["id"],
                "100",
            )

            self.assertEqual(
                records[1]["id"],
                "101",
            )


if __name__ == "__main__":
    unittest.main()