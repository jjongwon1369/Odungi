# Dataset Card — Matter / connectedhomeip Corpus

## Dataset name

Matter / connectedhomeip Corpus

## Version

Corpus v0.1, documented as a v1.0 candidate. It is not frozen because the licensing and team cross-review
gates have not passed.

## Purpose

Provide one fixed, provenance-preserving source corpus for fair comparison of single RAG, decomposed RAG,
and LLM Wiki systems. The systems should vary their processing, not their underlying evidence.

## Domain

Matter smart-home device data models, SDK/code-generation definitions, implementations, documentation,
and examples for laundry washers, room air conditioners, refrigerators, and supporting temperature-controlled cabinets.

## Source and snapshot

- Repository: `connectedhomeip`
- Observed branch: `master`
- Commit: `1ac132b5ecd42cb6c78772f2576ed6f7fc814183`
- Specification model baseline: `data_model/1.7`
- Snapshot ID: `corpus-v0.1:ee88b47ac7a901be55e52cb8039314b740d312dbff6982eec65bc3af6a735680`

The commit SHA, not the moving branch head, is the reproducibility boundary.

## Scope

Three product families, four Device Type IDs, and 23 unique clusters:

- Laundry Washer (`0x0073`)
- Room Air Conditioner (`0x0072`)
- Refrigerator (`0x0070`)
- Temperature Controlled Cabinet (`0x0071`, Cooler-only supporting scope)

## Composition

- 282 raw files
- 282 normalized documents
- 764 relations
- 342 entities
- 3,884,956 raw bytes
- 2,144,062 normalized characters

Source roles: 34 specification, 23 sdk_codegen, 185 implementation, 17 documentation, 20 example,
and 3 generated_definition files.

## Collection process

Paths were selected by the finalized `scope.json`. Files were read as Git blobs from the pinned commit,
not from a potentially newline-converted working tree. Each physical source path is stored once. Shared files
are linked to multiple device types or clusters through relations instead of being copied.

## Normalization

Common processing is limited to strict UTF-8 decoding, BOM removal, LF line endings, scope-controlled source
selection, and source-span mapping. It does not include chunking, embedding, summarization, Wiki compilation,
or benchmark-driven selection.

## Metadata

Each document records a stable path-based ID, source path and URL, commit, source role, definition kind,
source-specific revision, device/cluster bindings, raw and normalized SHA-256 hashes, and source spans.
Entity and relation files preserve requirements, conditions, assertion scope, and evidence.

## Known limitations

- Coverage has 21 accepted gaps: 20 missing standalone documentation entries and one unavailable concrete source.
- Source revisions are preserved separately; semantic equivalence across specification, SDK, examples, and code was not evaluated.
- Four relation evidence items are pinned upstream references rather than internal Corpus documents.
- Token count and context-window suitability are pending downstream model/tokenizer decisions.
- This Corpus does not establish specification conformance or runtime correctness.

## Missing documentation

Twenty coverage rows lack standalone Markdown in nine scoped component directories. This indicates absence in
the recorded search scope, not extraction failure and not absence of implementation code. The remaining missing
row is Temperature Alarm, for which the snapshot supplies specification material but no concrete SDK/implementation/IDL source.

## License / redistribution status

This card is not legal advice or a distribution authorization. Per-source review records 217 sources as
conditionally `redistributable`, 31 as `reference_only`, and 34 as `needs_review`. The complete raw/normalized
payload is not approved for public or external redistribution. Apache-2.0 files require applicable license,
NOTICE, copyright, and modification notices; CSA-marked specification XML and files without a detected per-file
notice require additional authority review. See `research/licensing_review.md` and `PUBLISHING.md`.

## Intended use

- Common evidence input for RAG and LLM Wiki research
- Retrieval, compilation, and provenance experiments within the authorized usage boundary
- Device Type/Cluster/source relationship analysis tied to the pinned snapshot

## Out-of-scope use

- Treating the data as an official stable Matter specification release
- Publicly redistributing the complete payload without rights review
- Claiming certification, conformance, runtime correctness, answer accuracy, or benchmark quality
- Inferring that optional/conditional requirements are enabled in a product
- Using benchmark questions or Gold Answers as Corpus construction input

## Reproducibility

The pipeline requires Python 3.10+, Git, and a clean checkout at the pinned commit. It verifies source identity,
manifest/raw hashes, normalized spans, identifiers, metadata, relations, coverage, and two independent rebuilds.
The current run reports 14 passing checks, 3 documented warnings, 0 failures, and 13 passing unit tests.
Commands and constraints are documented in `scripts/corpus/README.md`.
