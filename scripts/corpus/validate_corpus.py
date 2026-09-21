"""Verify corpus artifacts against source evidence and two independent rebuilds."""
from __future__ import annotations

from collections import Counter, defaultdict
import csv
import json
from pathlib import Path
import tempfile

from corpus_utils import (PROJECT_ROOT, Selection, canonical, canonical_text, digest, document_id,
                          json_bytes, load_json, require, writable_path, write_file)
from normalize_corpus import inventory, normalize


def read_jsonl(path):
    return [json.loads(line) for line in Path(path).read_text(encoding='utf-8').splitlines() if line.strip()]


def unique_ids(rows, field):
    values = [r[field] for r in rows]
    duplicate = [key for key, count in Counter(values).items() if count > 1]
    require(not duplicate, f'Duplicate {field}: {duplicate}')
    return len(values)


def verify_hash(data, expected, label):
    require(digest(data) == expected, 'Hash mismatch: ' + label)


def fingerprint(root, snapshot_name='snapshot.json'):
    """Includes IDs, relation sets, raw SHA256 and normalized text hashes.

    Compare serialized metadata too, so span/revision changes cannot hide behind
    otherwise matching text. Reports are run results, not corpus inputs.
    """
    names = ['metadata/corpus_manifest.csv', 'metadata/relations.jsonl', 'metadata/entities.jsonl',
             'metadata/statistics.json', 'metadata/' + snapshot_name, 'processed/documents.jsonl']
    hashes = {name: digest((root / name).read_bytes()) for name in names}
    hashes.update({p.relative_to(root).as_posix(): digest(p.read_bytes())
                   for p in (root / 'raw/connectedhomeip').rglob('*') if p.is_file()})
    return hashes


def rebuild_check(selection, actual_root=None, snapshot_name='snapshot.json'):
    from extract_corpus import Build
    results = []
    # Temporary directories are confined to the writable project; never source.
    for _ in range(2):
        with tempfile.TemporaryDirectory(prefix='.corpus-rebuild-', dir=PROJECT_ROOT) as directory:
            root = writable_path(directory, selection.repo.root)
            fresh = Selection(selection.repo, selection.scope_path)
            build = Build(fresh)
            build.write(root / 'raw', root / 'metadata' / snapshot_name)
            results.append(fingerprint(root, snapshot_name))
    require(results[0] == results[1], 'Two independent rebuilds differ')
    if actual_root is not None:
        require(results[0] == fingerprint(actual_root, snapshot_name), 'Current corpus differs from deterministic rebuild')
    return dict(builds=2, compared_files=len(results[0]), artifact_set_hash=digest(canonical(results[0]).encode()),
                document_ids='identical', relations='identical', raw_sha256='identical', normalized_hashes='identical')


def validate(selection, output, snapshot, rebuild=True, write_report=True):
    output = writable_path(output, selection.repo.root)
    snapshot = writable_path(snapshot, selection.repo.root)
    root, metadata = output.parent, snapshot.parent
    checks = {}

    def check(name, action):
        try:
            detail = action()
            checks[name] = dict(status='pass', message=name.replace('_', ' ') + ' verified', details=detail)
            return detail
        except (ValueError, KeyError, TypeError, OSError, IndexError, StopIteration) as exc:
            checks[name] = dict(status='fail', message=str(exc), details={})
            return None

    def warning(name, message, details):
        checks[name] = dict(status='warning', message=message, details=details)

    check('source_commit_match', lambda: selection.repo.verify())
    check('scope_file_existence', lambda: [selection.repo.check_file(p) for p in selection.files] and len(selection.files))
    with_errors = False
    try:
        with (metadata / 'corpus_manifest.csv').open(encoding='utf-8', newline='') as file:
            manifest = list(csv.DictReader(file))
        documents = read_jsonl(root / 'processed/documents.jsonl')
        relations = read_jsonl(metadata / 'relations.jsonl')
        entities = read_jsonl(metadata / 'entities.jsonl')
        actual_snapshot = load_json(snapshot)
    except (ValueError, OSError) as exc:
        checks['artifact_readability'] = dict(status='fail', message=str(exc), details={})
        with_errors = True
    if not with_errors:
        check('duplicate_document_id', lambda: unique_ids(manifest, 'document_id'))
        check('duplicate_normalized_document_id', lambda: unique_ids(documents, 'document_id'))
        check('duplicate_relation_id', lambda: unique_ids(relations, 'relation_id'))
        hashes = defaultdict(list)
        for row in manifest:
            hashes[row['content_hash']].append(row['source_path'])
        duplicates = {key: paths for key, paths in hashes.items() if len(paths) > 1}
        if duplicates:
            warning('duplicate_raw_hash', 'Same bytes at distinct allowed source paths; provenance files retained', duplicates)
        else:
            check('duplicate_raw_hash', lambda: {'duplicate_groups': 0})

        def raw_consistency():
            paths = [r['source_path'] for r in manifest]
            require(len(paths) == len(set(paths)), 'Duplicate physical source path')
            require(set(paths) == set(selection.files), 'Manifest file set differs from finalized scope')
            actual = {p.relative_to(output / 'connectedhomeip').as_posix()
                      for p in (output / 'connectedhomeip').rglob('*') if p.is_file()}
            require(actual == set(paths), 'Raw file set differs from manifest (missing/unexpected files)')
            for row in manifest:
                require(row['document_id'] == document_id(row['source_path']), 'Invalid stable document ID')
                require(row['raw_path'] == 'raw/connectedhomeip/' + row['source_path'], 'Invalid raw path')
                p = writable_path(root / row['raw_path'], selection.repo.root)
                verify_hash(p.read_bytes(), row['content_hash'], row['source_path'])
                require(p.read_bytes() == selection.repo.read(row['source_path']), 'Raw bytes differ from committed Git blob')
            return {'files': len(paths), 'unexpected': [], 'missing': []}

        check('manifest_raw_consistency_and_hash_validity', raw_consistency)

        def metadata_check():
            required = {'document_id', 'source_kind', 'source_role', 'definition_kind', 'source_path', 'raw_path',
                        'commit_hash', 'source_revision', 'doc_type', 'device_types', 'clusters', 'content_hash', 'included_reason'}
            for row in manifest:
                require(required <= row.keys(), 'Required manifest field missing')
                require(row['commit_hash'] == selection.repo.head, 'Manifest commit mismatch')
                for key in ['device_types', 'clusters', 'included_reason']:
                    require(isinstance(json.loads(row[key]), list), 'Invalid JSON array: ' + key)
                revision = json.loads(row['source_revision'])
                require(revision['artifact']['value'] == selection.repo.head, 'Revision artifact commit mismatch')
                require(isinstance(revision['declarations'], list), 'Missing revision declarations')
            require(actual_snapshot['snapshot_id'] == selection.snapshot_id, 'Snapshot ID mismatch')
            require(actual_snapshot['scope_hash'] == selection.scope_hash, 'Scope changed')
            require(actual_snapshot['coverage_hash'] == selection.coverage_hash, 'Coverage changed')
            return {'manifest_rows': len(manifest)}

        check('required_metadata', metadata_check)

        def spans_check():
            require({d['document_id'] for d in documents} == {m['document_id'] for m in manifest}, 'Document/manifest IDs differ')
            count = 0
            for doc in documents:
                path = doc['metadata']['source_path']
                require(path in selection.files, 'Unexpected normalized source')
                text = canonical_text(selection.repo.read(path))
                parts, previous = [], 0
                require(bool(doc['source_spans']), 'Missing source spans')
                for span in doc['source_spans']:
                    a, b = span['char_start'], span['char_end']
                    require(span['source_path'] == path and 0 <= a < b <= len(text) and a >= previous, 'Invalid span offsets')
                    require(span['line_start'] == text.count('\n', 0, a) + 1 and
                            span['line_end'] == text.count('\n', 0, b - 1) + 1, 'Invalid span line range')
                    previous = b
                    parts.append(text[a:b])
                    count += 1
                require('\n'.join(parts) == doc['text'], 'Normalized text is not the declared source excerpts')
                expected = normalize(path, selection.repo.read(path), selection)
                require(doc['source_spans'] == expected['source_spans'], 'Spans differ from scope selectors')
                verify_hash(doc['text'].encode('utf-8'), doc['metadata']['normalized_hash'], path + ' normalized')
                require(doc['snapshot_id'] == selection.snapshot_id, 'Normalized snapshot mismatch')
            return {'spans': count, 'documents': len(documents)}

        check('source_span_validity', spans_check)

        def identifier_check():
            count = 0
            for doc in documents:
                path = doc['metadata']['source_path']
                expected = normalize(path, selection.repo.read(path), selection)
                # Independent count over original selected slices, not saved inventory.
                source = canonical_text(selection.repo.read(path))
                original = Counter()
                for span in expected['source_spans']:
                    original.update(inventory(source[span['char_start']:span['char_end']]))
                require(original == inventory(doc['text']), 'Identifier preservation failed: ' + path)
                require(dict(original) == doc['metadata']['identifier_inventory'], 'Saved identifier inventory differs: ' + path)
                count += sum(original.values())
            return {'identifier_occurrences': count, 'comparison': 'selected original spans vs normalized lexical inventory',
                    'semantic_conformance_evaluated': False}

        check('identifier_preservation', identifier_check)

        def relation_check():
            keys = {canonical(e) for e in entities}
            require(len(keys) == len(entities), 'Duplicate entity')
            docids = {r['document_id'] for r in manifest}
            for relation in relations:
                require({'relation_id', 'relation_type', 'source_entity', 'target_entity', 'document_id',
                         'role', 'requirement', 'condition', 'evidence'} <= relation.keys(), 'Missing relation metadata')
                for e in [relation['source_entity'], relation['target_entity']] + relation.get('via_entities', []):
                    require(canonical(e) in keys, 'Dangling entity reference')
                    if e['kind'] == 'source_document':
                        require(e['id'] in docids, 'Dangling document entity')
                require(relation['document_id'] in docids, 'Dangling relation document')
                require(bool(relation['evidence']), 'Relation has no evidence')
                require(relation['requirement'] in {None, 'mandatory', 'optional', 'conditional', 'provisional',
                                                    'disallowed', 'not_applicable'}, 'Invalid requirement enum')
                for evidence in relation['evidence']:
                    path = evidence['source_path']
                    data = selection.repo.read(path)
                    verify_hash(data, evidence['content_hash'], path + ' evidence')
                    require(evidence['commit_sha'] == selection.repo.head, 'Evidence commit mismatch')
                    require(1 <= evidence['line_start'] <= len(canonical_text(data).splitlines()), 'Invalid evidence line')
                    if evidence['storage'] == 'corpus':
                        require(evidence['document_id'] in docids, 'Dangling evidence document')
                    else:
                        require(evidence['document_id'] is None and path not in selection.files, 'Invalid upstream-only evidence')
            return {'relations': len(relations), 'entities': len(entities)}

        check('relation_target_validity', relation_check)

        def revision_check():
            bypath = {r['source_path']: json.loads(r['source_revision']) for r in manifest}
            count = 0
            for cid, cl in selection.clusters.items():
                for field, revkey in [('specification_path', 'specification_revision'), ('sdk_definition_path', 'sdk_revision')]:
                    if cl[field] not in bypath:
                        continue
                    values = {d['value'] for d in bypath[cl[field]]['declarations']
                              if d['entity_kind'] == 'cluster' and d['entity_id'] == f'0x{cid:04X}'}
                    require(values == {cl[revkey]}, f'Scope/source revision differs for {cid}: {field}: {values}')
                    count += 1
            return {'verified_source_declarations': count, 'policy': 'compare each source to its own declared revision, not each other'}

        check('source_revision_declarations', revision_check)

        def coverage_check():
            require({r['coverage_id'] for r in selection.included} ==
                    {c for r in relations for c in r.get('coverage_ids', [])}, 'Coverage relation rows differ')
            required = [r for r in relations if r['relation_type'] == 'requires_cluster']
            require(len(required) == 42, 'Expected 42 device-cluster relations')
            ids = {r['target_entity']['id'] for r in required}
            require(ids == {f'0x{c:04X}' for c in selection.clusters}, 'Expected 23 covered clusters')
            # All metadata and relations are regenerated from fixed inputs. This
            # checks correct targets/conditions, not merely referential integrity.
            from extract_corpus import Build
            expected = Build(Selection(selection.repo, selection.scope_path))
            expected_manifest = [{k: canonical(v) if isinstance(v, (list, dict)) else v for k, v in row.items()}
                                 for row in expected.manifest]
            require(manifest == expected_manifest, 'Manifest metadata differs from pinned sources and scope')
            require(relations == expected.relations, 'Relation assertions differ from pinned sources and coverage')
            require(documents == expected.documents, 'Normalized metadata differs from pinned source selection')
            require(entities == expected.entities, 'Entity registry differs from scope')
            require(load_json(metadata / 'statistics.json') == expected.statistics, 'Statistics differ')
            require(actual_snapshot == expected.snapshot, 'Snapshot metadata differs')
            return {'unique_clusters': len(ids), 'device_cluster_relations': 42, 'coverage_rows': len(selection.coverage),
                    'included_rows': len(selection.included), 'excluded_rows': len(selection.coverage) - len(selection.included)}

        check('coverage_matrix_consistency', coverage_check)
        missing = [r['coverage_id'] for r in selection.included if r['status'] == 'missing']
        if missing:
            warning('accepted_coverage_gaps', 'Finalized gaps retained; no missing source files fabricated',
                    {'coverage_ids': missing, 'count': len(missing), 'temperature_alarm': 'specification only; no concrete SDK/implementation/IDL',
                     'documentation': '20 repeated rows: standalone Markdown absent in nine scoped component directories'})
        warning('revision_semantics', 'Source-specific revisions preserved; numerical differences are not automatically errors',
                {'semantic_consistency': 'not evaluated', 'baseline': 'development data_model/1.7'})
        warning('token_measurement', 'Token count pending tokenizer/model choice', {'token_count': None})
        if rebuild:
            check('deterministic_rebuild', lambda: rebuild_check(selection, root, snapshot.name))
        else:
            warning('deterministic_rebuild', 'Rebuild deliberately skipped for this test invocation', {})
    status = 'fail' if any(c['status'] == 'fail' for c in checks.values()) else (
        'warning' if any(c['status'] == 'warning' for c in checks.values()) else 'pass')
    report = dict(snapshot_id=selection.snapshot_id, status=status, checks=checks,
                  summary=dict(Counter(c['status'] for c in checks.values())))
    if write_report:
        write_file(metadata / 'validation_report.json', json_bytes(report), selection.repo.root)
    return report


if __name__ == '__main__':
    from extract_corpus import main
    import sys
    if '--validate-only' not in sys.argv:
        sys.argv.append('--validate-only')
    raise SystemExit(main())
