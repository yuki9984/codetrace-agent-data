# Zenodo deposit checklist

This checklist prepares the primary archival dataset record. It does not authorize publication.

## 1. Start a draft

1. Sign in to Zenodo.
2. Open **My dashboard** and select **New upload**.
3. Choose **Dataset** as the resource type.
4. Keep the record as a draft until every gate below is complete.

## 2. Upload the verified primary archive

Upload one file:

`CodeTrace-Agent-1000-sanitized.zip`

Expected size: 8,790,519,112 bytes  
Expected SHA-256: `ff359f3cda0f1ef5cb5b3cfb84e801592c4494e7dafff68fa964baa3f7c12d9d`

After upload, compare the file size and checksum with `checksums/CodeTrace-Agent-1000-sanitized.SHA256.txt`. Stop if either value differs.

## 3. Enter metadata

Provisional title:

> CodeTrace-Agent: One thousand Python software engineering environments linked to execution records

Complete and verify all of the following before publication:

- creators in final publication order;
- ORCID identifiers where available;
- affiliations and corresponding author details;
- final release date and version;
- English description and keywords;
- funding and related project identifiers, if applicable;
- access rights;
- a licence and rights statement approved for all deposited components.

Do not infer a licence from upstream source-code files. The deposit may contain components under different upstream licences and team-created metadata or documentation under a separate approved licence.

## 4. Record provenance and relations

Add the fixed historical Hugging Face revision as a related identifier using an `isDerivedFrom` relationship:

`https://huggingface.co/datasets/yuki99981/codetrace-agent-1000-instances/tree/b3142c640f1766efa368dec2d1421dc1d90b210f`

After the GitHub repository becomes public, add its permanent release or archived software identifier as a related resource. Add the manuscript DOI only after the manuscript has one.

## 5. Save, reserve, and publish in separate steps

1. Save the draft and perform a metadata review.
2. Reserve a DOI only after the creator list, version, rights, and deposit structure are approved.
3. Update the manuscript and data citation with the reserved DOI.
4. Do not select **Publish** until the final archive, metadata, companion materials, and author approvals are complete.

Publication is a separate irreversible release decision; a saved draft or reserved DOI is not evidence that the dataset is publicly available.

## 6. Post-publication acceptance test

From a clean environment:

1. download the public archive from its DOI landing page;
2. verify the complete ZIP checksum;
3. verify the embedded manifest and exact archive membership;
4. run the predeclared normal and known-failure reuse examples;
5. preserve the environment, commands, raw logs, results, and final receipt.

Only after this test passes should the manuscript describe the DOI deposit as independently downloadable and reuse-tested.

