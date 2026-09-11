# CodeTrace-Agent GitHub Release fallback

This is an optional mirror workflow. The formal data record should use the immutable archive and persistent identifier selected by the authors.

## Files to download

Download `RELEASE-ASSET-PARTS.json` and all five files named `CodeTrace-Agent-1000-sanitized.zip.part001` through `.part005` into one otherwise-empty directory. Keep `split_release_asset.py` outside that directory.

## Verify the five parts

```text
python split_release_asset.py verify --manifest <parts-directory>/RELEASE-ASSET-PARTS.json
```

The expected result is `parts_verified`, five parts and 8,790,519,112 verified bytes. Stop if verification fails.

## Reassemble the archive

```text
python split_release_asset.py reassemble --manifest <parts-directory>/RELEASE-ASSET-PARTS.json --output <destination>/CodeTrace-Agent-1000-sanitized.zip
```

The reassembled ZIP must have SHA-256:

```text
ff359f3cda0f1ef5cb5b3cfb84e801592c4494e7dafff68fa964baa3f7c12d9d
```

Only after this check passes should the archive be extracted and its embedded `SHA256SUMS.json` verifier be used. Do not use a Git clone, Git LFS pointer checkout or a third-party Hugging Face mirror as a substitute for these five complete binary assets.

For a reuse trial, complete acquisition and integrity checks before installing or starting Docker and Harbor. Preserve every attempt separately.
