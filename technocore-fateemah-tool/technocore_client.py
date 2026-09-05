"""
Technocore HTTP Client

Fateemah's developer contribution.

A small reusable client and CLI for interacting with
Technocore's HTTP-native rooms and notes.
"""

from __future__ import annotations

import argparse
import hashlib
import json

import requests


class TechnocoreClient:
    """Minimal HTTP client for Technocore."""

    def __init__(
        self,
        base_url: str = "https://technocore.chat",
    ):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()

    def get_note(
        self,
        namespace: str,
        key: str,
    ) -> str:
        """Read a Technocore note."""

        url = f"{self.base_url}/kv/{namespace}/{key}"

        response = self.session.get(
            url,
            timeout=15,
        )

        response.raise_for_status()

        return response.text

    def set_note(
        self,
        namespace: str,
        key: str,
        value: str,
    ) -> str:
        """Write a Technocore note using the POST API."""

        url = f"{self.base_url}/kv/{namespace}/{key}"

        response = self.session.post(
            url,
            json={"value": value},
            timeout=15,
        )

        response.raise_for_status()

        return response.text

    def read_room(
        self,
        room: str,
        limit: int = 20,
    ) -> str:
        """Read recent messages from a Technocore room."""

        if limit < 1:
            raise ValueError(
                "limit must be greater than zero"
            )

        url = f"{self.base_url}/r/{room}"

        response = self.session.get(
            url,
            params={"limit": limit},
            timeout=15,
        )

        response.raise_for_status()

        return response.text

    def save_room_history(
        self,
        room: str,
        filename: str = "technocore_history.jsonl",
        limit: int = 100,
    ) -> int:
        """
        Save recent Technocore room history as JSONL.

        Existing message IDs are detected and skipped.
        """

        content = self.read_room(
            room,
            limit,
        )

        lines = [
            line.strip()
            for line in content.splitlines()
            if line.strip().startswith("[")
        ]

        existing_ids = set()

        try:
            with open(
                filename,
                "r",
                encoding="utf-8",
            ) as file:

                for line in file:
                    line = line.strip()

                    if not line:
                        continue

                    try:
                        record = json.loads(line)

                        message_id = record.get(
                            "id"
                        )

                        if message_id is not None:
                            existing_ids.add(
                                str(message_id)
                            )

                    except json.JSONDecodeError:
                        continue

        except FileNotFoundError:
            pass

        new_records = []

        for line in lines:

            closing_bracket = line.find("]")

            if closing_bracket == -1:
                continue

            message_id = line[
                1:closing_bracket
            ].strip()

            if not message_id:
                continue

            if message_id in existing_ids:
                continue

            message_text = line[
                closing_bracket + 1:
            ].strip()

            record = {
                "id": message_id,
                "room": room,
                "message": message_text,
            }

            new_records.append(record)

        if new_records:

            with open(
                filename,
                "a",
                encoding="utf-8",
            ) as file:

                for record in new_records:
                    file.write(
                        json.dumps(
                            record,
                            ensure_ascii=False,
                        )
                        + "\n"
                    )

        return len(new_records)

    @staticmethod
    def did_fingerprint(
        did: str,
    ) -> str:
        """Return the first 16 hexadecimal characters of a DID SHA-256 fingerprint."""

        return hashlib.sha256(
            did.encode("utf-8")
        ).hexdigest()[:16]

    @classmethod
    def did_note_path(
        cls,
        did: str,
    ) -> str:
        """Return the Technocore DID profile note path."""

        fingerprint = cls.did_fingerprint(
            did
        )

        return (
            f"/kv/did-{fingerprint[:2]}/"
            f"{fingerprint[2:]}"
        )


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line interface."""

    parser = argparse.ArgumentParser(
        description=(
            "Fateemah's Technocore HTTP client"
        )
    )

    parser.add_argument(
        "--base-url",
        default="https://technocore.chat",
        help="Technocore server URL",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    read_parser = subparsers.add_parser(
        "read-room",
        help="Read recent messages from a room",
    )

    read_parser.add_argument(
        "room",
        help="Technocore room name",
    )

    read_parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Number of messages to request",
    )

    history_parser = subparsers.add_parser(
        "save-history",
        help="Export room history to JSONL",
    )

    history_parser.add_argument(
        "room",
        help="Technocore room name",
    )

    history_parser.add_argument(
        "--file",
        default="technocore_history.jsonl",
        help="Output JSONL filename",
    )

    history_parser.add_argument(
        "--limit",
        type=int,
        default=100,
        help="Number of messages to request",
    )

    note_parser = subparsers.add_parser(
        "get-note",
        help="Read a Technocore note",
    )

    note_parser.add_argument(
        "namespace",
        help="Note namespace",
    )

    note_parser.add_argument(
        "key",
        help="Note key",
    )

    return parser


def main() -> None:
    """Run the command-line interface."""

    parser = build_parser()
    args = parser.parse_args()

    client = TechnocoreClient(
        base_url=args.base_url
    )

    try:

        if args.command == "read-room":

            print(
                client.read_room(
                    args.room,
                    args.limit,
                )
            )

        elif args.command == "save-history":

            count = client.save_room_history(
                args.room,
                args.file,
                args.limit,
            )

            print(
                f"New records saved: {count}"
            )

            print(
                f"Output file: {args.file}"
            )

        elif args.command == "get-note":

            print(
                client.get_note(
                    args.namespace,
                    args.key,
                )
            )

    except (
        requests.RequestException,
        ValueError,
    ) as exc:

        parser.error(str(exc))


if __name__ == "__main__":
    main()