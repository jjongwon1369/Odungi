"""Read-only corpus review; writes audit records, never changes frozen inputs.

Run from project root: python scripts/corpus_review/freeze_audit.py
Kept outside scripts/corpus to leave the extraction pipeline fingerprint intact.
"""
from collections import Counter
import csv
import json
from pathlib import Path, PurePosixPath
import re
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts/corpus'))
from corpus_utils import Repository, Selection, canonical_text, digest, document_id, json_bytes, require, write_file
from validate_corpus import read_jsonl


def main():
    repo = Repository(ROOT.parent / 'connectedhomeip')
    base = ROOT / 'corpus'
    selection = Selection(repo, base / 'metadata/scope.json')
    manifest = list(csv.DictReader((base / 'metadata/corpus_manifest.csv').open(encoding='utf-8', newline='')))
    docs = read_jsonl(base / 'processed/documents.jsonl')
    relations = read_jsonl(base / 'metadata/relations.jsonl')
    snapshot = json.loads((base / 'metadata/snapshot.json').read_text(encoding='utf-8'))
    byid = {m['document_id']: m for m in manifest}
    require(len(byid) == len(manifest) == len(docs) == 282, 'Document count/uniqueness differs')
    roles, types, devices, clusters = Counter(), Counter(), Counter(), Counter()
    raw_bytes, characters = 0, 0
    license_rows, revision_rows = [], []
    for doc in docs:
        row = byid[doc['document_id']]
        path = row['source_path']
        require(document_id(path) == doc['document_id'], 'Invalid document identity')
        require(row['commit_hash'] == repo.head, 'Commit differs')
        raw = (base / row['raw_path']).read_bytes()
        require(raw == repo.read(path) and digest(raw) == row['content_hash'], 'Invalid raw provenance')
        text = canonical_text(raw)
        selected = []
        for span in doc['source_spans']:
            require(span['source_path'] == path, 'Span path differs')
            a, b = span['char_start'], span['char_end']
            require(0 <= a < b <= len(text), 'Span out of range')
            selected.append(text[a:b])
        require('\n'.join(selected) == doc['text'], 'Exact source characters changed')
        require(digest(doc['text'].encode()) == doc['metadata']['normalized_hash'], 'Normalized hash differs')
        for key, value in row.items():
            parsed = json.loads(value) if key in {'source_revision', 'device_types', 'clusters', 'included_reason'} else value
            require(doc['metadata'][key] == parsed, 'Manifest/metadata differs: ' + key)
        rev = json.loads(row['source_revision'])
        require(rev['artifact']['value'] == repo.head, 'Revision provenance differs')
        revision_rows.append(dict(document_id=row['document_id'], source_path=path, source_role=row['source_role'],
                                  source_revision=rev))
        head = text[:10000]
        if 'own internal purposes' in head and 'post or publish this document' in head:
            license_class, review = 'CSA_document_specific_restrictions', 'needs_review'
        elif 'Apache License' in head or 'SPDX-License-Identifier: Apache-2.0' in head:
            license_class, review = 'Apache-2.0_explicit_notice', 'conditional_redistribution'
        else:
            license_class, review = 'no_explicit_file_license_detected', 'needs_review'
        license_rows.append(dict(document_id=row['document_id'], source_path=path, content_hash=row['content_hash'],
                                 license_class=license_class, status=review,
                                 evidence_lines=[i for i, line in enumerate(text.splitlines(), 1)
                                                 if any(t in line for t in ['Apache License', 'own internal purposes',
                                                                           'post or publish', 'SPDX-License-Identifier'])]))
        roles[row['source_role']] += 1
        types[row['doc_type']] += 1
        devices.update(json.loads(row['device_types']))
        clusters.update(json.loads(row['clusters']))
        raw_bytes += len(raw)
        characters += len(doc['text'])
    stats = json.loads((base / 'metadata/statistics.json').read_text())
    recomputed = dict(unique_file_count=len(manifest), normalized_document_count=len(docs), relation_count=len(relations),
                      by_source_role=dict(roles), by_doc_type=dict(types), by_device_type=dict(devices), by_cluster=dict(clusters),
                      raw_byte_size=raw_bytes, normalized_character_count=characters)
    for key, value in recomputed.items():
        require(stats[key] == value, 'Statistics differ: ' + key)

    missing_rows = []
    for row in selection.coverage:
        if row['status'] != 'missing':
            continue
        if row['coverage_id'] == 'C039':
            category = 'unavailable_source'
            evidence = dict(specification_path=row['specification_path'], specification_lines=[60, 66, 67],
                            sdk_include_path='src/app/zap-templates/zcl/data-model/chip/matter-devices.xml', sdk_include_line=3263,
                            search_roots=['src/app/clusters', 'src/app/zap-templates/zcl/data-model/chip',
                                          'zzz_generated/app-common/clusters'],
                            selected_idls=[p for p in selection.scope['example_rules']['artifacts'] if p.endswith('.matter')])
            # Search text in bounded committed files; report every hit, not a guessed absence.
            matches = []
            candidates = [p for p in repo.entries if any(p.startswith(r + '/') for r in evidence['search_roots'])
                          and PurePosixPath(p).suffix in {'.cpp', '.h', '.xml', '.md'}]
            candidates += [p for p in selection.scope['example_rules']['artifacts'] if p.endswith('.matter')]
            repo.read_many(candidates)
            for path in sorted(candidates):
                for line, value in enumerate(canonical_text(repo.read(path)).splitlines(), 1):
                    if re.search(r'Temperature.?Alarm|0x0064', value, re.I):
                        matches.append(dict(path=path, line=line, text=value.strip(),
                                            hit_kind='generator_parameter_comment' if value.lstrip().startswith('Parameters:')
                                            else 'device_include_reference' if '<include cluster="Temperature Alarm"' in value
                                            else 'requires_inspection'))
            evidence.update(search_pattern='Temperature.?Alarm|0x0064 (case insensitive)',
                            searched_files=len(candidates), matches=matches)
            sdk_definitions, idl_definitions = [], []
            def numeric(value):
                value = value.strip()
                return int(value, 16 if value.lower().startswith('0x') else 10)
            for path in candidates:
                text = canonical_text(repo.read(path))
                if path.startswith('src/app/zap-templates/zcl/data-model/chip/') and path.endswith('.xml'):
                    tree = ET.fromstring(text)
                    for cluster in tree.findall('./cluster'):
                        code = cluster.findtext('code')
                        if code and numeric(code) == 100:
                            sdk_definitions.append(path)
                elif path.endswith('.matter'):
                    for match in re.finditer(r'\bcluster\s+\w+\s*=\s*(0[xX][0-9A-Fa-f]+|\d+)\s*\{', text):
                        if numeric(match[1]) == 100:
                            idl_definitions.append(dict(path=path, line=text.count('\n', 0, match.start()) + 1))
            require(not sdk_definitions and not idl_definitions, 'Temperature Alarm definitions found; review missing classification')
            evidence.update(structured_sdk_cluster_definitions=sdk_definitions,
                            selected_idl_cluster_definitions=idl_definitions,
                            numeric_id_checked=100)
            reason = 'Selected snapshot has a provisional specification and SDK device include; concrete definition/implementation/IDL unavailable in bounded search. No global not-implemented claim.'
        else:
            category = 'documentation_missing'
            directory = str(PurePosixPath(row['implementation_path']).parent)
            matches = [p for p in repo.entries if str(PurePosixPath(p).parent) == directory and p.endswith('.md')]
            require(not matches, 'Documentation now exists: ' + directory)
            repo.check_file(row['implementation_path'])
            evidence = dict(existing_implementation=row['implementation_path'], search_directory=directory,
                            pattern='*.md', recursive=False, matches=matches)
            reason = 'Implementation and definitions exist; no standalone Markdown file immediately under this component directory. Does not assert absence of comments or broader guides.'
        missing_rows.append(dict(coverage_id=row['coverage_id'], device_type=row['device_type_name'], cluster=row['cluster_name'],
                                 classification=category, evidence=evidence, reason=reason, scope_changed=False))
    require(len(missing_rows) == 21, 'Missing row count changed')

    external, count, coarse = [], 0, 0
    for relation in relations:
        require(relation['document_id'] in byid, 'Relation primary document missing')
        for ev in relation['evidence']:
            count += 1
            raw = repo.read(ev['source_path'])
            require(digest(raw) == ev['content_hash'] and ev['commit_sha'] == repo.head, 'Evidence provenance mismatch')
            require(1 <= ev['line_start'] <= len(canonical_text(raw).splitlines()), 'Invalid evidence line')
            if ev['storage'] == 'corpus':
                require(ev['document_id'] in byid and byid[ev['document_id']]['source_path'] == ev['source_path'], 'Evidence document mismatch')
            else:
                external.append(dict(relation_id=relation['relation_id'], coverage_ids=relation.get('coverage_ids'), evidence=ev))
            if ev['locator'] == 'file':
                coarse += 1
    report = dict(snapshot_id=snapshot['snapshot_id'], commit_hash=repo.head,
                  audit_script_path='scripts/corpus_review/freeze_audit.py', audit_script_hash=digest(Path(__file__).read_bytes()),
                  statistics_recomputed=recomputed, statistics_match=True,
                  document_provenance=dict(status='pass', count=len(docs), chain='document_id -> manifest -> raw_path -> source_path -> committed Git blob'),
                  identifier_preservation=dict(status='pass', documents=len(docs),
                     method='Exact character equality of all selected source spans to normalized text, including names/IDs and code identifiers; only recorded LF separators added',
                     semantic_evaluation=False, excluded_raw_regions='outside normalized scope, not a preservation failure'),
                  source_revision=dict(status='pass', manifest_metadata_equal=True, records=revision_rows,
                                       policy='Source-specific declarations retained; no semantic comparison'),
                  relation_provenance=dict(primary_documents='pass', primary_document_count=len(relations), evidence_count=count,
                                           external_evidence=external, file_level_locator_count=coarse,
                                           all_evidence_has_corpus_document=not external,
                                           status='needs_review' if external else 'pass'),
                  missing_analysis=dict(counts=dict(Counter(r['classification'] for r in missing_rows)), rows=missing_rows),
                  license_inventory=dict(counts=dict(Counter(r['license_class'] for r in license_rows)), rows=license_rows),
                  external_documents=[r['source_path'] for r in manifest if r['source_kind'] != 'repository'],
                  licensing_sources=[dict(path=p, commit_hash=repo.head, content_hash=digest(repo.read(p))) for p in ['LICENSE', 'NOTICE']])
    write_file(base / 'metadata/freeze_audit.json', json_bytes(report), repo.root)
    lines = ['# Coverage missing 분석', '', f'고정 commit: `{repo.head}`. Scope와 기존 CSV 상태는 변경하지 않았다.', '',
             '분류 결과: documentation_missing 20, unavailable_source 1, expected_missing 0, not_implemented 0, scope_issue 0.', '',
             '`expected_missing`은 원래 대상이 아닌 자료를 기대한 경우, `not_implemented`는 미구현을 명시적으로 입증한 경우에만 사용한다.',
             '허용된 결손이라는 사실 자체를 expected_missing으로 바꾸지 않는다. 검색 부재는 전역 미구현의 증거가 아니다.', '',
             '| Coverage | Device Type / Cluster | 분류 | 실제 근거 및 이유 |', '|---|---|---|---|']
    for r in missing_rows:
        e = r['evidence']
        evidence = (f"`{e['existing_implementation']}` 존재; `{e['search_directory']}/*.md` 비재귀 검색 0건. 독립 가이드 부재이며 구현 부재가 아니다."
                    if r['classification'] == 'documentation_missing' else
                    '`data_model/1.7/clusters/TemperatureAlarm.xml:60–67`의 provisional 정의, `src/app/zap-templates/zcl/data-model/chip/matter-devices.xml:3263`의 include만 확인. concrete SDK/구현/IDL은 지정 검색 범위에서 발견되지 않음.')
        lines.append(f"| {r['coverage_id']} | {r['device_type']} / {r['cluster']} | {r['classification']} | {evidence} |")
    lines += ['', 'C039는 documentation_missing도 동반하지만 주 분류는 unavailable_source다. 공통 Alarm Base를 concrete Temperature Alarm 구현으로 대체하지 않는다.',
              '검색 범위·파일 수·모든 검색 hit 및 행별 근거는 [freeze_audit.json](../metadata/freeze_audit.json)의 missing_analysis에 기록했다.',
              '현재 21행에서 Scope 자체의 모순은 확인하지 못했다. 분류는 이 commit과 명시된 검색 범위에 한정한다.']
    write_file(base / 'research/missing_analysis.md', ('\n'.join(lines) + '\n').encode(), repo.root)
    repo.verify()
    print(json.dumps({k: report[k] for k in ['statistics_match', 'document_provenance', 'identifier_preservation']}, indent=2))
    print(json.dumps(dict(licenses=report['license_inventory']['counts'], missing=report['missing_analysis']['counts'],
                          evidence_count=count, external_evidence_count=len(external), file_level_locators=coarse), indent=2))


if __name__ == '__main__':
    main()
