#!/usr/bin/env python3
"""Reassemble the versioned Hilbert theorem-search source file.

The GitHub connector used for the initial archival upload stored the long
reference implementation as six ordered UTF-8 source parts. This script joins
them byte-for-byte and verifies the expected SHA-256 digest.
"""

from __future__ import annotations

from hashlib import sha256
from pathlib import Path

EXPECTED_SHA256 = "ae4f61c1dabcac69d25d0e3cd3c602a1e23196bbd6227c165f58251776151eab"


def main() -> None:
    root = Path(__file__).resolve().parent
    parts = sorted((root / "source_parts").glob("hilbert_theorem_search.part_*.py.part"))
    if len(parts) != 6:
        raise SystemExit(f"Expected 6 source parts, found {len(parts)}")

    output = root / "hilbert_theorem_search.py"
    payload = b"".join(part.read_bytes() for part in parts)
    digest = sha256(payload).hexdigest()
    if digest != EXPECTED_SHA256:
        raise SystemExit(
            "Source-part checksum mismatch: "
            f"expected {EXPECTED_SHA256}, observed {digest}"
        )

    output.write_bytes(payload)
    print(f"Wrote {output.name} ({len(payload):,} bytes)")
    print(f"SHA-256: {digest}")


if __name__ == "__main__":
    main()
