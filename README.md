# CodeTrace-Agent data release

This is the private staging repository for the data, validation materials, and release tooling associated with the CodeTrace-Agent Data Descriptor.

## Release status

- The repository is a private staging area and is not yet the authoritative public data record.
- No DOI has been registered and no GitHub Release has been published.
- The historical frozen dataset and its existing Hugging Face commit remain unchanged.
- The sanitized publication archive has been built and verified locally. Its binary archive is intentionally not stored in Git history.

## Prepared archive

The intended primary deposit is the single archive:

`CodeTrace-Agent-1000-sanitized.zip`

Expected size: 8,790,519,112 bytes  
Expected SHA-256: `ff359f3cda0f1ef5cb5b3cfb84e801592c4494e7dafff68fa964baa3f7c12d9d`

The primary archival route is a Zenodo dataset deposit. A GitHub Release can provide an optional mirror using five independently verifiable parts. The parts, their sizes, and their hashes are listed in `release-assets/RELEASE-ASSET-PARTS.json`.

## Repository contents

- `checksums/`: checksum for the complete sanitized ZIP.
- `docs/`: instructions for verifying and reconstructing the optional split GitHub Release assets.
- `release-assets/`: manifest for the five local release parts. The large binary parts are excluded from Git history.
- `tools/`: the tested split, verify, and reassembly utility.

## Important interpretation note

The published record must distinguish historical build-time validation from later revalidation. The dataset must not be described as if all 1,000 instances are currently executable without qualification. Final manuscript wording, repository metadata, licensing, authorship, DOI, and public download smoke-test evidence remain publication gates.

## Citation and licence

Citation metadata and licence information will be added only after the authors approve the final creators, affiliations, version, repository metadata, and rights statement. Do not cite this private staging repository as the final dataset record.

