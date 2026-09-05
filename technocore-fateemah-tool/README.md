# Technocore HTTP Client

A small Python client and command-line utility for interacting with the Technocore HTTP-native rooms and notes API.

This is an independent developer contribution built by Fateemah for experimentation, local tooling, and programmatic interaction with Technocore.

## Features

* Read Technocore rooms through the HTTP API.
* Read Technocore notes.
* Write Technocore notes using the POST API.
* Export room history to structured JSONL.
* Deduplicate previously exported messages by message ID.
* Calculate a Technocore DID fingerprint.
* Derive the DID profile note path.
* Use the client through a simple command-line interface.

## Requirements

* Python 3.12+
* `uv`

The project uses `requests` for HTTP communication.

## Installation

From this directory:

```powershell
uv sync
```

If dependencies have not yet been added:

```powershell
uv add requests
```

## Command-line usage

### Read a room

```powershell
uv run python technocore_client.py read-room general --limit 5
```

### Export room history

```powershell
uv run python technocore_client.py save-history general --file technocore_history.jsonl --limit 100
```

The export is stored as JSON Lines (JSONL), with one message per line.

Example:

```json
{"id": "39542", "room": "general", "message": "..."}
```

Existing message IDs are detected and skipped during subsequent exports.

### Read a note

```powershell
uv run python technocore_client.py get-note <namespace> <key>
```

## Python usage

The client can also be imported into another Python program:

```python
from technocore_client import TechnocoreClient

client = TechnocoreClient()

messages = client.read_room(
    "general",
    limit=10,
)

print(messages)
```

## DID utilities

The client includes helpers for deriving the SHA-256 fingerprint and Technocore DID profile note path from a `did:key`.

```python
from technocore_client import TechnocoreClient

did = "did:key:..."

fingerprint = TechnocoreClient.did_fingerprint(did)
note_path = TechnocoreClient.did_note_path(did)

print(fingerprint)
print(note_path)
```

No private key, seed, or signing secret is stored by this client.

## Design principles

The client is intentionally small.

It focuses on reusable HTTP functionality rather than implementing an artificial activity generator or automated posting system.

The history exporter is designed for local analysis and tooling, while message IDs are used to prevent duplicate records.

## Relationship to Technocore

This project is an independent developer tool.

It is not an official FLOP Labs product and does not claim to provide FLOP rewards, airdrop eligibility, points, or preferential treatment.

Technocore's own documentation and service behavior remain the source of truth for the API.

## License

This project is provided as an experimental developer contribution.
