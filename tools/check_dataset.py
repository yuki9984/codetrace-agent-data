"""Recognize a registered CodeTrace dataset edition, then verify its payload."""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import subprocess
import sys

KNOWN_MANIFESTS = {
    "9909915d332e8cefdfe66ec5a3f3b6b466fdea0555d818e985ddb8d5d0ef7312": "hf-fixed-source",
    "3662096b3dd57fd50766636a16034dac9ce328ad43e5351b3664ca1cd382b044": "zenodo-sanitized-derivative-v1-draft",
}


def identify_digest(digest: str) -> str:
    edition = KNOWN_MANIFESTS.get(digest)
    if edition is None:
        raise ValueError(f"Unknown dataset manifest SHA-256: {digest}")
    return edition


def identify_manifest(path: Path) -> tuple[str, str]:
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    edition = identify_digest(digest)
    return edition, digest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset", type=Path)
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()
    root = args.dataset.resolve()
    manifest = root / "SHA256SUMS.json"
    if not manifest.is_file():
        parser.error("Dataset manifest is missing")
    try:
        edition, digest = identify_manifest(manifest)
    except (OSError, ValueError) as exc:
        parser.exit(2, f"{exc}\n")
    print(f"Recognized dataset edition: {edition}")
    print(f"Manifest SHA-256: {digest}")
    return subprocess.run(
        [sys.executable, "-B", str(Path(__file__).with_name("verify_bundle.py")), str(root), "--workers", str(args.workers)],
        check=False,
    ).returncode


if __name__ == "__main__":
    raise SystemExit(main())
