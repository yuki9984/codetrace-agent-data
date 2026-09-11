from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


SCHEMA = "codetrace-release-asset-parts-v1"
DEFAULT_PART_BYTES = 1900 * 1024 * 1024
BUFFER_BYTES = 4 * 1024 * 1024


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(BUFFER_BYTES), b""):
            digest.update(block)
    return digest.hexdigest()


def load_manifest(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if value.get("schema") != SCHEMA or not isinstance(value.get("parts"), list):
        raise ValueError("Invalid release-parts manifest")
    return value


def split(source: Path, output_directory: Path, expected_sha256: str, part_bytes: int) -> dict:
    source = source.resolve()
    output_directory = output_directory.resolve()
    if not source.is_file() or part_bytes <= 0:
        raise ValueError("Source archive is unavailable or part size is invalid")
    if len(expected_sha256) != 64:
        raise ValueError("Expected source SHA-256 must contain 64 hexadecimal characters")
    if output_directory.exists():
        raise FileExistsError("Refusing to reuse an existing output directory")
    output_directory.mkdir(parents=True)

    source_digest = hashlib.sha256()
    rows: list[dict] = []
    total = 0
    with source.open("rb") as input_stream:
        index = 1
        while True:
            first = input_stream.read(min(BUFFER_BYTES, part_bytes))
            if not first:
                break
            part_name = f"{source.name}.part{index:03d}"
            part_path = output_directory / part_name
            part_digest = hashlib.sha256()
            written = 0
            with part_path.open("xb") as output_stream:
                block = first
                while block:
                    output_stream.write(block)
                    part_digest.update(block)
                    source_digest.update(block)
                    written += len(block)
                    total += len(block)
                    remaining = part_bytes - written
                    if remaining == 0:
                        break
                    block = input_stream.read(min(BUFFER_BYTES, remaining))
            rows.append({"name": part_name, "bytes": written, "sha256": part_digest.hexdigest()})
            index += 1

    actual_sha256 = source_digest.hexdigest()
    if actual_sha256.lower() != expected_sha256.lower():
        raise ValueError("Source archive SHA-256 does not match the approved receipt")
    manifest = {
        "schema": SCHEMA,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "parts_created_locally_not_uploaded",
        "source": {"name": source.name, "bytes": total, "sha256": actual_sha256},
        "part_size_limit_bytes": part_bytes,
        "part_count": len(rows),
        "parts": rows,
        "public_upload_performed": False,
    }
    manifest_path = output_directory / "RELEASE-ASSET-PARTS.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    return manifest


def verify(manifest_path: Path) -> dict:
    manifest_path = manifest_path.resolve()
    manifest = load_manifest(manifest_path)
    root = manifest_path.parent
    expected_names = {"RELEASE-ASSET-PARTS.json"} | {row["name"] for row in manifest["parts"]}
    actual_names = {path.name for path in root.iterdir() if path.is_file()}
    if actual_names != expected_names:
        raise ValueError("Release-parts directory membership mismatch")
    if manifest["part_count"] != len(manifest["parts"]):
        raise ValueError("Release-parts count mismatch")
    total = 0
    for index, row in enumerate(manifest["parts"], start=1):
        expected_name = f"{manifest['source']['name']}.part{index:03d}"
        path = root / row["name"]
        if row["name"] != expected_name or not path.is_file():
            raise ValueError("Release-part sequence mismatch")
        if path.stat().st_size != row["bytes"] or sha256(path) != row["sha256"]:
            raise ValueError(f"Release-part integrity mismatch: {row['name']}")
        if row["bytes"] > manifest["part_size_limit_bytes"]:
            raise ValueError(f"Release part exceeds configured limit: {row['name']}")
        total += row["bytes"]
    if total != manifest["source"]["bytes"]:
        raise ValueError("Release-parts total byte count mismatch")
    return {"status": "parts_verified", "part_count": len(manifest["parts"]), "bytes_verified": total}


def reassemble(manifest_path: Path, output: Path) -> dict:
    manifest_path = manifest_path.resolve()
    manifest = load_manifest(manifest_path)
    verify(manifest_path)
    output = output.resolve()
    partial = output.with_name(output.name + ".partial")
    if output.exists() or partial.exists():
        raise FileExistsError("Refusing to overwrite an existing reassembled file or partial file")
    digest = hashlib.sha256()
    total = 0
    with partial.open("xb") as destination:
        for row in manifest["parts"]:
            with (manifest_path.parent / row["name"]).open("rb") as source:
                for block in iter(lambda: source.read(BUFFER_BYTES), b""):
                    destination.write(block)
                    digest.update(block)
                    total += len(block)
    actual_sha256 = digest.hexdigest()
    if total != manifest["source"]["bytes"] or actual_sha256 != manifest["source"]["sha256"]:
        raise ValueError("Reassembled archive does not match the source binding; partial file retained")
    partial.replace(output)
    return {"status": "reassembled", "output": str(output), "bytes": total, "sha256": actual_sha256}


def main() -> None:
    parser = argparse.ArgumentParser(description="Split, verify or reassemble a large immutable release asset without uploading it.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    split_parser = subparsers.add_parser("split")
    split_parser.add_argument("--source", type=Path, required=True)
    split_parser.add_argument("--output-directory", type=Path, required=True)
    split_parser.add_argument("--expected-sha256", required=True)
    split_parser.add_argument("--part-bytes", type=int, default=DEFAULT_PART_BYTES)
    verify_parser = subparsers.add_parser("verify")
    verify_parser.add_argument("--manifest", type=Path, required=True)
    reassemble_parser = subparsers.add_parser("reassemble")
    reassemble_parser.add_argument("--manifest", type=Path, required=True)
    reassemble_parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    if args.command == "split":
        result = split(args.source, args.output_directory, args.expected_sha256, args.part_bytes)
    elif args.command == "verify":
        result = verify(args.manifest)
    else:
        result = reassemble(args.manifest, args.output)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, FileNotFoundError, FileExistsError, OSError) as error:
        raise SystemExit(str(error))
