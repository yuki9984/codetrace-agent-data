from __future__ import annotations

import importlib.util
from pathlib import Path, PurePosixPath
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


check_dataset = load("check_dataset", ROOT / "tools" / "check_dataset.py")
verify_bundle = load("verify_bundle", ROOT / "tools" / "verify_bundle.py")


class ManifestRecognitionTests(unittest.TestCase):
    def test_hf_manifest_is_registered(self):
        self.assertEqual(check_dataset.identify_digest("9909915d332e8cefdfe66ec5a3f3b6b466fdea0555d818e985ddb8d5d0ef7312"), "hf-fixed-source")

    def test_zenodo_draft_manifest_is_registered(self):
        self.assertEqual(check_dataset.identify_digest("3662096b3dd57fd50766636a16034dac9ce328ad43e5351b3664ca1cd382b044"), "zenodo-sanitized-derivative-v1-draft")

    def test_unknown_manifest_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Unknown dataset manifest"):
            check_dataset.identify_digest("0" * 64)


class FileSetTests(unittest.TestCase):
    def test_client_metadata_is_ignored(self):
        self.assertTrue(verify_bundle.should_include(PurePosixPath("instances/task/file.txt")))
        for folder in verify_bundle.IGNORED_TOP_LEVEL:
            self.assertFalse(verify_bundle.should_include(PurePosixPath(folder) / "metadata.bin"))

    def test_added_and_missing_payloads_are_reported(self):
        difference = verify_bundle.compare_file_sets({"kept", "missing"}, {"kept", "added"})
        self.assertEqual(difference, {"missing": ["missing"], "unexpected": ["added"]})

    def test_modified_file_hash_is_detectable(self):
        self.assertNotEqual(verify_bundle.sha256_bytes(b"before"), verify_bundle.sha256_bytes(b"after"))


if __name__ == "__main__":
    unittest.main()
