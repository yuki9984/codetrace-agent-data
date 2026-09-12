# CodeTrace-Agent-1000 release materials

This public repository provides lightweight code, documentation, checksums, and validation metadata for the CodeTrace-Agent-1000 dataset. The 8.79 GB primary archive is deposited separately in Zenodo and is not stored in Git history.

## Current release status

- Dataset version DOI assigned in a Zenodo draft: `10.5281/zenodo.22701046`.
- The Zenodo record is not yet publicly resolvable. Treat the DOI as reserved until the record has been published and independently downloaded.
- Frozen source dataset: Hugging Face commit `b3142c640f1766efa368dec2d1421dc1d90b210f`.
- Historical construction-time result: 1,000/1,000 tasks met the original release gates.
- Later primary-host replay: 993/1,000 met the dual-gate condition; seven retained tasks have explicit failure records.

These statements describe different validation times. This repository does not claim that all 1,000 tasks currently execute successfully on every host.

## Prepared archive

Expected file:

`CodeTrace-Agent-1000-sanitized.zip`

Expected size: 8,790,519,112 bytes  
Expected SHA-256: `ff359f3cda0f1ef5cb5b3cfb84e801592c4494e7dafff68fa964baa3f7c12d9d`

After Zenodo publication, download the archive from the version record and verify it before extraction. Do not rely on the browser archive preview for completeness.

## Repository contents

- `checksums/`: checksum for the complete sanitized ZIP.
- `metadata/instance-status.json`: machine-readable status for all 1,000 tasks.
- `tools/verify_bundle.py`: bundle verification utility.
- `docs/`: integrity, reuse, and optional fallback instructions.
- `release-assets/`: manifest for an optional five-part mirror. The parts are unnecessary while Zenodo is available and are excluded from Git history.

## Reuse boundary

Use `instance_id` to join tasks, trajectories, and validation records. Read stored trajectory reward separately from later replay status. A valid test failure is scientific evidence and must not be rewritten as an infrastructure failure; an interrupted download, Docker failure, or unavailable dependency must be recorded separately.

## Licence

Original verification and release software is provided under the MIT License. Team-created dataset metadata, indices, annotations, and documentation are designated CC BY 4.0. Embedded upstream source snapshots remain governed by their retained per-instance licences and notices.

## Citation

Until the Zenodo record is publicly released, cite the fixed Hugging Face revision and describe `10.5281/zenodo.22701046` as an assigned draft DOI. Replace this instruction with the formal Zenodo citation only after public resolution and download verification.
