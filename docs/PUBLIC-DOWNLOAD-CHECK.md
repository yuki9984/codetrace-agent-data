# Public download verification

Run this check only after the Zenodo record is publicly resolvable without a preview token.

1. Open `https://doi.org/10.5281/zenodo.22701046` in a signed-out browser.
2. Download `CodeTrace-Agent-1000-sanitized.zip` into a new empty directory.
3. Confirm a size of 8,790,519,112 bytes.
4. Compute SHA-256 and require `ff359f3cda0f1ef5cb5b3cfb84e801592c4494e7dafff68fa964baa3f7c12d9d`.
5. Preserve the first download and its log. Do not overwrite a failed or interrupted attempt.
6. Extract only after the archive-level hash passes, then run the included manifest verifier.

A preview URL or owner session does not demonstrate anonymous reviewer access. The check remains incomplete while the public Zenodo API returns 404 for the record.
