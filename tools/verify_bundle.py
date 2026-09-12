from __future__ import annotations

import argparse
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

IGNORED_TOP_LEVEL = frozenset({".git", ".huggingface", ".cache"})


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def should_include(relative: Path) -> bool:
    return not (set(relative.parts) & IGNORED_TOP_LEVEL)


def collect_actual_files(root: Path, manifest_path: Path) -> dict[str, Path]:
    """Collect payload files while excluding downloader/VCS metadata."""
    return {
        path.relative_to(root).as_posix(): path
        for path in root.rglob("*")
        if path.is_file()
        and path != manifest_path
        and should_include(path.relative_to(root))
    }


def compare_file_sets(declared: set[str], actual: set[str]) -> dict[str, list[str]]:
    return {
        "missing": sorted(declared - actual),
        "unexpected": sorted(actual - declared),
    }


def verify(root: Path, workers: int) -> dict[str, Any]:
    errors: list[dict[str, Any]] = []
    manifest_path = root / "SHA256SUMS.json"
    index_path = root / "instance-trajectory-index.json"
    quality_path = root / "quality-report.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        index = json.loads(index_path.read_text(encoding="utf-8"))
        quality = json.loads(quality_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"valid": False, "errors": [{"code": "metadata_unreadable", "detail": str(exc)}]}

    rows = list(index.get("instances") or [])
    ids = [str(row.get("instance_id") or "") for row in rows]
    contents = [str(row.get("content_sha256") or "") for row in rows]
    trajectories = [str(row.get("trajectory_path") or "") for row in rows]
    if index.get("submission_unit") != "instance":
        errors.append({"code": "submission_unit_not_instance"})
    if len(rows) != 1000 or len(set(ids)) != 1000 or "" in ids:
        errors.append({"code": "instance_cardinality_invalid"})
    if len(set(contents)) != 1000 or "" in contents:
        errors.append({"code": "instance_content_hashes_not_unique"})
    if len(set(trajectories)) != 1000 or "" in trajectories:
        errors.append({"code": "trajectory_mapping_not_one_to_one"})

    gates = quality.get("quality_gates") or {}
    required_gates = (
        "nop_reward_zero",
        "oracle_reward_one",
        "unique_ids",
        "unique_content_hashes",
        "one_hash_matched_complete_trajectory_per_instance",
    )
    if quality.get("instance_count") != 1000 or quality.get("trajectory_count") != 1000:
        errors.append({"code": "quality_cardinality_invalid"})
    if any(gates.get(name) is not True for name in required_gates):
        errors.append({"code": "quality_gate_failed"})

    for row in rows:
        instance_id = str(row.get("instance_id") or "")
        instance_dir = root / str(row.get("instance_path") or "")
        trajectory_path = root / str(row.get("trajectory_path") or "")
        if not instance_dir.is_dir():
            errors.append({"code": "instance_missing", "instance_id": instance_id})
            continue
        try:
            trajectory = json.loads(trajectory_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            errors.append({"code": "trajectory_unreadable", "instance_id": instance_id})
            continue
        evaluation = trajectory.get("evaluation") or {}
        reward = trajectory.get("final_reward")
        expected_status = "passed" if reward == 1 else "failed"
        if (
            trajectory.get("task_id") != instance_id
            or trajectory.get("task_sha256") != row.get("content_sha256")
            or trajectory.get("status") != expected_status
            or evaluation.get("valid") is not bool(reward)
            or not trajectory.get("completed_at")
            or not trajectory.get("steps")
        ):
            errors.append({"code": "trajectory_binding_invalid", "instance_id": instance_id})
        if sha256_file(trajectory_path) != row.get("trajectory_sha256"):
            errors.append({"code": "trajectory_sha256_mismatch", "instance_id": instance_id})

    declared = {str(row.get("path")): row for row in manifest.get("files", [])}
    actual = collect_actual_files(root, manifest_path)
    file_set_difference = compare_file_sets(set(declared), set(actual))
    if file_set_difference["missing"] or file_set_difference["unexpected"]:
        errors.append(
            {
                "code": "manifest_file_set_mismatch",
                "declared": len(declared),
                "actual": len(actual),
                "missing": file_set_difference["missing"][:20],
                "unexpected": file_set_difference["unexpected"][:20],
            }
        )

    def check_file(relative: str) -> dict[str, Any] | None:
        path = actual[relative]
        expected = declared[relative]
        if path.stat().st_size != expected.get("bytes") or sha256_file(path) != expected.get("sha256"):
            return {"code": "file_integrity_mismatch", "path": relative}
        return None

    common = sorted(set(declared) & set(actual))
    with ThreadPoolExecutor(max_workers=max(1, workers)) as executor:
        errors.extend(error for error in executor.map(check_file, common) if error is not None)
    return {
        "schema_version": "codetrace-public-bundle-verification-v1",
        "valid": not errors,
        "instance_count": len(rows),
        "trajectory_count": len(trajectories),
        "declared_file_count": len(declared),
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify a downloaded CodeTrace-Agent HF dataset bundle.")
    parser.add_argument("root", nargs="?", default=".", type=Path)
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()
    report = verify(args.root.resolve(), args.workers)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["valid"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
