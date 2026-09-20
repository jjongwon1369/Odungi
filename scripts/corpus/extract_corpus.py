"""Build a deterministic Corpus v0.1 from the finalized local scope (stdlib)."""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re
import sys

from corpus_utils import (CorpusError, Repository, Selection, SENTINELS, canonical, canonical_text,
                          csv_bytes, digest, document_id, json_bytes, jsonl_bytes, pipeline_hash,
                          require, stable_id, writable_path, write_file)
from normalize_corpus import (child_value, descendants, normalize, number, xml_tree)


def hexid(value):
    return f'0x{value:04X}'


def entity(kind, value, namespace='matter'):
    return dict(kind=kind, namespace=namespace, id=value)


def revision_declarations(path, text, selection):
    result = []

    def add(kind, eid, scheme, value, pos, locator):
        if value is not None:
            result.append(dict(entity_kind=kind, entity_id=eid, scheme=scheme, value=str(value),
                               status='present', locator=locator, line_start=text.count('\n', 0, pos) + 1))

    if path.endswith('.xml'):
        root = xml_tree(text)
        if root['name'] in {'cluster', 'deviceType'}:
            if root['name'] == 'cluster':
                ids = [n['attrs']['id'] for n in descendants(root, 'clusterId')
                       if 'id' in n['attrs'] and number(n['attrs']['id']) in selection.clusters]
                kind, scheme = ('cluster', 'cluster_revision') if ids else ('cluster_base', 'cluster_revision')
            else:
                ids = [hexid(pid) for pid, p in selection.products.items() if p['definition_path'] == path]
                kind, scheme = ('device_type', 'device_type_revision') if ids else ('device_type_base', 'device_type_revision')
                if path.endswith('RootNodeDeviceType.xml'):
                    ids, kind = ['0x0016'], 'device_type'
            symbolic = {'ModeBase': 'Mode Base', 'AlarmBase': 'Alarm Base', 'Label-Cluster': 'Label'}.get(Path(path).stem, Path(path).stem)
            for eid in ids or [symbolic]:
                add(kind, eid, scheme, root['attrs'].get('revision'), root['start'], '/' + root['name'] + '/@revision')
        else:
            for n in root['children']:
                if n['name'] == 'cluster':
                    code = child_value(n, 'code', text)
                    if code and number(code) in selection.clusters:
                        for attr in descendants(n, 'globalAttribute'):
                            if number(attr['attrs'].get('code', '0')) == 0xFFFD:
                                add('cluster', hexid(number(code)), 'cluster_revision', attr['attrs'].get('value'),
                                    attr['start'], '/configurator/cluster/globalAttribute[@code="0xFFFD"]')
                if n['name'] == 'deviceType':
                    code = child_value(n, 'deviceId', text)
                    if code and number(code) in selection.products:
                        add('device_type', hexid(number(code)), 'device_type_revision', child_value(n, 'revision', text),
                            n['start'], '/configurator/deviceType/revision')
    elif path.endswith('.matter'):
        for m in re.finditer(r'\bcluster\s+\w+\s*=\s*(\d+)\s*\{\s*revision\s+(\d+)', text):
            if number(m[1]) in selection.clusters:
                add('cluster', hexid(number(m[1])), 'cluster_revision', m[2], m.start(), 'cluster/revision')
        for m in re.finditer(r'device\s+type\s+\w+\s*=\s*(\d+),\s*version\s+(\d+)', text):
            if number(m[1]) in selection.products:
                add('device_type', hexid(number(m[1])), 'device_type_revision', m[2], m.start(), 'endpoint/device type/version')
    elif path.endswith('.zap'):
        from normalize_corpus import json_tree
        tree = json_tree(text)
        groups = next(n for n in tree['children'] if n['key'] == 'endpointTypes')
        generic = '/all-clusters-app/' in path
        for i, node in enumerate(groups['children']):
            ep = node['value']
            ids = ep.get('deviceIdentifiers', [])
            pids = {number(v) for v in ids} & set(selection.products)
            if not pids and not generic:
                continue
            for pid, rev in zip(ids, ep.get('deviceVersions', [])):
                if number(pid) in pids:
                    add('device_type', hexid(number(pid)), 'device_type_revision', rev, node['start'], f'$.endpointTypes[{i}].deviceVersions')
            allowed = set(selection.clusters) if generic else set().union(*(selection.allowed_for_device(p) for p in pids))
            for j, cl in enumerate(ep.get('clusters', [])):
                cid = number(cl['code'])
                if cid in allowed:
                    for k, attr in enumerate(cl.get('attributes', [])):
                        if number(attr['code']) == 0xFFFD:
                            add('cluster', hexid(cid), 'configured_cluster_revision', attr.get('defaultValue'),
                                node['start'], f'$.endpointTypes[{i}].clusters[{j}].attributes[{k}]')
    elif path.startswith('zzz_generated/'):
        ids = selection.files[path]['clusters']
        m = re.search(r'kRevision\s*=\s*(\d+)', text)
        if m:
            for cid in sorted(ids):
                add('cluster', hexid(cid), 'cluster_revision', m[1], m.start(), 'kRevision')
    return sorted(result, key=canonical)


def enrich_bindings(selection):
    # Propagate explicit, source-declared bindings to paired artifacts and allowed
    # supporting files. This changes metadata only, never physical file selection.
    rows = [r for r in selection.included if r['relation_type'] == 'requires_cluster']
    for path, info in selection.files.items():
        if path.endswith(('.matter', '.zap')):
            text = canonical_text(selection.repo.read(path))
            if path.endswith('.zap'):
                ids = {number(v) for ep in json.loads(text)['endpointTypes'] for v in ep.get('deviceIdentifiers', [])}
            else:
                ids = {number(v) for v in re.findall(r'device\s+type\s+\w+\s*=\s*(\d+)', text)}
            info['device_types'].update(ids & selection.products.keys())
            normalized = normalize(path, selection.repo.read(path), selection)['text']
            if path.endswith('.matter'):
                cids = {number(v) for v in re.findall(r'\bcluster\s+\w+\s*=\s*(\d+)', normalized)}
            else:
                # Cluster configuration objects selected by the source-span parser.
                doc = normalize(path, selection.repo.read(path), selection)
                cids = {number(json.loads(canonical_text(selection.repo.read(path))[s['char_start']:s['char_end']])['code'])
                        for s in doc['source_spans'] if re.search(r'\.clusters\[\d+\]$', s['locator'])}
            info['clusters'].update(cids & selection.clusters.keys())
            # All-clusters is cluster evidence for these devices, not a claim that
            # its endpoints declare those Device Types.
            for row in rows:
                if number(row['cluster_id']) in info['clusters']:
                    info['device_types'].add(number(row['device_type_id']))
        if path.startswith('zzz_generated/'):
            text = canonical_text(selection.repo.read(path))
            m = re.search(r'cluster code:\s*(\d+)/0x[0-9a-fA-F]+', text)
            require(m is not None, f'Missing generated cluster ID: {path}')
            for row in rows:
                if number(row['cluster_id']) == number(m[1]):
                    selection.bind(path, row['device_type_id'], row['cluster_id'])
        if path.endswith('DefaultServerCluster.h') or path.endswith('SpecificationDefinedRevisions.h'):
            info['device_types'].update(selection.products)
            info['clusters'].update(selection.clusters)
        if path.endswith('/ModeBase.xml') or path.endswith('/AlarmBase.xml') or path.endswith('/Label-Cluster.xml'):
            continue
        # Paired header/source files on the explicit allowlist use the same binding.
        if path in selection.scope['example_rules']['implementation_allowlist']:
            for other, binding in selection.files.items():
                if Path(other).stem == Path(path).stem and other != path:
                    info['device_types'].update(binding['device_types'])
                    info['clusters'].update(binding['clusters'])
            if '/laundry-washer-app/' in path or 'laundry-washer-' in Path(path).name:
                info['device_types'].add(0x73)
            if 'static-supported-temperature-levels' in path:
                info['device_types'].update({0x70, 0x71})
                info['clusters'].add(0x56)
        if path.endswith('/CMakeLists.txt'):
            info['device_types'].add(0x73)
            info['clusters'].update({0x51, 0x53})


class Graph:
    def __init__(self, selection):
        self.s = selection
        self.entities, self.relations = {}, {}

    def register(self, value):
        self.entities[canonical(value)] = value
        return value

    def evidence(self, path, line=None, locator=None):
        data = self.s.repo.read(path)
        text = canonical_text(data)
        if line is not None:
            require(1 <= int(line) <= len(text.splitlines()), f'Invalid evidence line: {path}:{line}')
        result = dict(source_path=path, commit_sha=self.s.repo.head, content_hash=digest(data),
                      line_start=int(line) if line else 1, locator=locator or 'file')
        if path in self.s.files:
            result.update(document_id=document_id(path), source_role=self.s.files[path]['source_role'], storage='corpus')
        else:
            result.update(document_id=None, source_role='implementation', storage='upstream_reference_only')
        return result

    def add(self, kind, source, target, path, evidence=None, **extra):
        require(path in self.s.files, f'Relation primary document outside scope: {path}')
        ev = evidence or [self.evidence(path)]
        record = dict(relation_type=kind, source_entity=self.register(source), target_entity=self.register(target),
                      document_id=document_id(path), role=None, requirement=None, condition=None,
                      evidence=ev, assertion_scope=self.s.files[path]['source_role'], status='present')
        record.update(extra)
        record['relation_id'] = stable_id('rel', [self.s.repo.head, record])
        self.relations[record['relation_id']] = record
        return record

    def build(self):
        for path in self.s.files:
            self.register(entity('source_document', document_id(path), 'connectedhomeip'))
        for row in self.s.included:
            pid = row['device_type_id']
            source = entity('device_type', pid)
            kind = row['relation_type']
            ev = [self.evidence(e['path'], e.get('line'), e.get('selector')) for e in json.loads(row['evidence_location'])]
            primary = next(e['source_path'] for e in ev if e['document_id'])
            condition = None if row['feature_condition'] in SENTINELS else {'op': 'source_expression', 'raw': row['feature_condition']}
            extra = dict(coverage_ids=[row['coverage_id']], role=None if row['server_client_role'] in SENTINELS else row['server_client_role'],
                         requirement=None if row['requirement'] in SENTINELS else row['requirement'], condition=condition)
            extra['requirement_raw'] = row['requirement']
            requirement = row['requirement']
            extra['requirement'] = ('not_applicable' if requirement in SENTINELS else
                                    'conditional' if 'conditional' in requirement else
                                    'mandatory' if requirement in {'required', 'mandatory'} else requirement)
            if kind == 'requires_cluster':
                target = entity('cluster', row['cluster_id'])
                primary = ('data_model/1.7/device_types/BaseDeviceType.xml' if row['relationship_origin'] == 'base'
                           else row['device_type_definition_path'])
                text = canonical_text(self.s.repo.read(primary))
                root = xml_tree(text)
                node = next(n for n in descendants(root, 'cluster')
                            if number(n['attrs'].get('id', '-1')) == number(row['cluster_id'])
                            and n['attrs'].get('side') == row['server_client_role'])
                conforms = [n for n in node['children'] if n['name'].endswith('Conform')]
                require(conforms, f'Missing conformance: {row["coverage_id"]}')

                def ast(n):
                    return dict(op=n['name'], attributes=n['attrs'], children=[ast(c) for c in n['children']])

                extra['condition'] = dict(op='conformance', ast=[ast(n) for n in conforms],
                                          raw='\n'.join(text[n['start']:n['end']] for n in conforms),
                                          coverage_expression=condition)
                extra['relationship_origin'] = row['relationship_origin']
                if row['relationship_origin'] == 'base':
                    extra['via_entities'] = [self.register(entity('device_type_base', 'BaseDeviceType'))]
                ev.insert(0, self.evidence(primary, text.count('\n', 0, node['start']) + 1,
                                           f'/deviceType/clusters/cluster[@id="{row["cluster_id"]}"]'))
            elif kind == 'requires_related_device_condition':
                target = entity('device_type', row['related_device_type'].split(':')[-1])
            elif kind == 'inherits_requirements':
                target = entity('device_type_base', 'BaseDeviceType')
            elif kind in {'requires_endpoint', 'requires_endpoint_scope'}:
                target = entity('endpoint_requirement', pid + ':' + kind)
                extra['endpoint_requirement'] = row['endpoint_requirement']
                if row['related_device_type'] not in SENTINELS:
                    extra['related_device_type'] = row['related_device_type']
            elif kind == 'example_composes_endpoint':
                endpoint = re.search(r'endpointId==(\d+)', ev[0]['locator'])[1]
                source = entity('example_endpoint', '1', primary)
                target = entity('example_endpoint', endpoint, primary)
                zap = json.loads(canonical_text(self.s.repo.read(primary)))
                require(any(e['endpointId'] == int(endpoint) and e['parentEndpointIdentifier'] == 1
                            for e in zap['endpoints']), 'Example composition evidence differs')
            elif kind == 'uses_shared_implementation':
                target = entity('implementation_component', 'src/app/clusters/mode-base-server', 'connectedhomeip')
                extra['via_entities'] = [self.register(entity('cluster', '0x0051' if pid == '0x0073' else
                                                              '0x0063' if pid == '0x0072' else '0x0052'))]
            else:
                raise CorpusError('Unsupported finalized relation: ' + kind)
            if pid == '0x0071':
                extra['scope_condition'] = dict(Cooler=True, Heater=False)
            self.add(kind, source, target, primary, ev, **extra)

        # Source-specific definitions remain separate assertions with separate revisions.
        for cid, cluster in self.s.clusters.items():
            cl = entity('cluster', hexid(cid))
            for field, kind in [('specification_path', 'defined_by_specification'),
                                ('sdk_definition_path', 'defined_by_sdk'), ('documentation_path', 'documented_by'),
                                ('idl_path', 'illustrated_by')]:
                path = cluster[field]
                if path not in SENTINELS:
                    self.add(kind, cl, entity('source_document', document_id(path), 'connectedhomeip'), path)
            path = cluster['implementation_path']
            if path not in SENTINELS:
                component = entity('implementation_component', str(Path(path).parent).replace('\\', '/'), 'connectedhomeip')
                self.add('implemented_by', cl, component, path, implementation_scope=cluster['implementation_scope'])
            spec = cluster['specification_path']
            root = xml_tree(canonical_text(self.s.repo.read(spec)))
            for n in descendants(root, 'classification'):
                base = n['attrs'].get('baseCluster')
                if base:
                    require(base in {'Mode Base', 'Alarm Base', 'Label'}, f'Unexpected base dependency: {base}')
                    self.add('derives_cluster_base', cl, entity('cluster_base', base), spec)
        for pid, product in self.s.products.items():
            path = product['definition_path']
            self.add('defined_by_specification', entity('device_type', hexid(pid)),
                     entity('source_document', document_id(path), 'connectedhomeip'), path)
            path = 'src/app/zap-templates/zcl/data-model/chip/matter-devices.xml'
            self.add('defined_by_sdk', entity('device_type', hexid(pid)),
                     entity('source_document', document_id(path), 'connectedhomeip'), path)
        for name, filename in [('Mode Base', 'ModeBase.xml'), ('Alarm Base', 'AlarmBase.xml'), ('Label', 'Label-Cluster.xml')]:
            path = 'data_model/1.7/clusters/' + filename
            self.add('defined_by_specification', entity('cluster_base', name),
                     entity('source_document', document_id(path), 'connectedhomeip'), path)
        path = 'src/app/zap-templates/zcl/data-model/chip/mode-base-cluster.xml'
        self.add('defined_by_sdk', entity('cluster_base', 'Mode Base'),
                 entity('source_document', document_id(path), 'connectedhomeip'), path)
        path = 'data_model/1.7/device_types/BaseDeviceType.xml'
        self.add('defined_by_specification', entity('device_type_base', 'BaseDeviceType'),
                 entity('source_document', document_id(path), 'connectedhomeip'), path)
        path = 'data_model/1.7/device_types/RootNodeDeviceType.xml'
        self.add('defined_by_specification', entity('device_type', '0x0016'),
                 entity('source_document', document_id(path), 'connectedhomeip'), path,
                 definition_extent='classification/revision/GroupcastListenerCond context only')
        for path, info in self.s.files.items():
            doc = entity('source_document', document_id(path), 'connectedhomeip')
            if path.startswith('src/app/clusters/') and info['source_role'] == 'implementation':
                component = entity('implementation_component', str(Path(path).parent).replace('\\', '/'), 'connectedhomeip')
                self.add('has_source_file', component, doc, path)
                for pid in sorted(info['device_types']):
                    # Membership is provenance, not a claim every method runs on every device.
                    self.add('uses_shared_implementation', entity('device_type', hexid(pid)), component, path,
                             via_entities=[self.register(entity('cluster', hexid(cid))) for cid in sorted(info['clusters'])],
                             derivation='finalized cluster mapping + declared component file membership')
            if info['source_role'] == 'example':
                for cid in sorted(info['clusters']):
                    self.add('illustrated_by', entity('cluster', hexid(cid)), doc, path)
            if info['source_role'] == 'generated_definition':
                for cid in sorted(info['clusters']):
                    impl = self.s.clusters[cid]['implementation_path']
                    component = entity('implementation_component', str(Path(impl).parent).replace('\\', '/'), 'connectedhomeip')
                    code = canonical_text(self.s.repo.read(impl))
                    namespace = Path(path).parent.name
                    require(namespace + '::kRevision' in code, f'Generated revision not referenced in {impl}')
                    pos = code.index(namespace + '::kRevision')
                    self.add('uses_revision_declaration', component, doc, path,
                             [self.evidence(impl, code.count('\n', 0, pos) + 1), self.evidence(path)])
        return sorted(self.entities.values(), key=canonical), sorted(self.relations.values(), key=lambda r: r['relation_id'])


class Build:
    def __init__(self, selection):
        self.selection = s = selection
        enrich_bindings(s)
        self.manifest, self.documents = [], []
        for path, info in sorted(s.files.items()):
            raw = s.repo.read(path)
            doc = normalize(path, raw, s)
            revisions = revision_declarations(path, canonical_text(raw), s)
            revision = dict(artifact=dict(scheme='git_commit', value=s.repo.head), declarations=revisions)
            if info['source_role'] == 'specification':
                revision.update(model_version='1.7', spec_sha=s.scope['repository']['spec_sha'], spec_tag=s.scope['repository']['spec_tag'])
            kind = Path(path).suffix.lstrip('.') or 'text'
            if path.endswith('CMakeLists.txt'):
                kind = 'cmake'
            devices = [hexid(i) for i in sorted(info['device_types'])]
            clusters = [hexid(i) for i in sorted(info['clusters'])]
            row = dict(document_id=document_id(path), source_kind='repository', source_role=info['source_role'],
                       definition_kind=info['definition_kind'], source_path=path,
                       raw_path='raw/connectedhomeip/' + path, commit_hash=s.repo.head, source_revision=revision,
                       doc_type=kind, device_types=devices, clusters=clusters, content_hash=digest(raw),
                       included_reason=sorted(info['reasons']))
            self.manifest.append(row)
            metadata = dict(row, source_id='connectedhomeip',
                            source_url='https://github.com/project-chip/connectedhomeip/blob/' + s.repo.head + '/' + path,
                            normalized_hash=doc['normalized_hash'], identifier_inventory=doc['identifier_inventory'],
                            entity_bindings=[entity('device_type', d) for d in devices] + [entity('cluster', c) for c in clusters],
                            offset_unit='unicode_codepoint_in_decoded_LF_source',
                            normalization='exact source excerpts joined by LF; not necessarily standalone parseable structured data')
            self.documents.append(dict(document_id=row['document_id'], snapshot_id=s.snapshot_id,
                                       text=doc['text'], metadata=metadata, source_spans=doc['source_spans']))
        self.entities, self.relations = Graph(s).build()
        self.snapshot = dict(snapshot_id=s.snapshot_id, corpus_version='0.1', frozen=False, commit_hash=s.repo.head,
                             origin=s.repo.remote, branch_observed=s.repo.branch, scope_hash=s.scope_hash,
                             coverage_hash=s.coverage_hash, pipeline_hash=pipeline_hash(), source_id='connectedhomeip',
                             raw_byte_origin='Git committed blob; no checkout newline conversion',
                             execution_authority='Explicit Corpus Extraction Pipeline request supersedes historical execution flags',
                             normalized_hash_scheme='SHA256 UTF-8 text', document_id_scheme='SHA256 canonical [source_id, relative_posix_path]')
        self.statistics = self.stats()

    def stats(self):
        s = self.selection
        def counts(field):
            return dict(sorted(Counter(r[field] for r in self.manifest).items()))
        def multivalued(field):
            return dict(sorted(Counter(v for r in self.manifest for v in r[field]).items()))
        return dict(unique_file_count=len(self.manifest), normalized_document_count=len(self.documents),
                    relation_count=len(self.relations), entity_count=len(self.entities),
                    by_source_role=counts('source_role'), by_doc_type=counts('doc_type'),
                    by_device_type=multivalued('device_types'), by_cluster=multivalued('clusters'),
                    grouping_policy='files may count for multiple devices/clusters; context-only files can have no binding',
                    raw_byte_size=sum(len(s.repo.read(p)) for p in s.files),
                    normalized_character_count=sum(len(d['text']) for d in self.documents),
                    expected_unique_clusters=23, extracted_unique_clusters=len({c for r in self.manifest for c in r['clusters']}),
                    missing=[r['coverage_id'] for r in s.included if r['status'] == 'missing'],
                    not_applicable=[r['coverage_id'] for r in s.coverage if r['status'] == 'not_applicable'],
                    missing_source_files=[], unexpected=[], token_count=None, tokenizer_status='pending model/tokenizer decision')

    def write(self, output, snapshot):
        s = self.selection
        output, snapshot = writable_path(output, s.repo.root), writable_path(snapshot, s.repo.root)
        require(output.name == 'raw' and snapshot.parent == output.parent / 'metadata',
                'Use <corpus-root>/raw and <corpus-root>/metadata/<snapshot>.json for portable paths')
        require(snapshot.name not in {'scope.json', 'statistics.json', 'validation_report.json'}
                and snapshot.suffix == '.json', 'Snapshot must not overwrite an input or another artifact')
        existing = output / 'connectedhomeip'
        if existing.exists():
            files = {p.relative_to(existing).as_posix() for p in existing.rglob('*') if p.is_file()}
            require(not files - s.files.keys(), 'Unexpected existing raw files; refusing to delete or expand scope')
        for path in sorted(s.files):
            write_file(existing / path, s.repo.read(path), s.repo.root)
        for filename, data in [('corpus_manifest.csv', csv_bytes(self.manifest)),
                               ('relations.jsonl', jsonl_bytes(self.relations)),
                               ('entities.jsonl', jsonl_bytes(self.entities)),
                               ('statistics.json', json_bytes(self.statistics))]:
            write_file(snapshot.parent / filename, data, s.repo.root)
        write_file(snapshot, json_bytes(self.snapshot), s.repo.root)
        write_file(output.parent / 'processed/documents.jsonl', jsonl_bytes(self.documents), s.repo.root)
        s.repo.verify()


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source-repo', required=True)
    p.add_argument('--scope', required=True)
    p.add_argument('--output', required=True)
    p.add_argument('--snapshot', required=True)
    group = p.add_mutually_exclusive_group()
    group.add_argument('--dry-run', action='store_true')
    group.add_argument('--validate-only', action='store_true')
    return p


def main():
    args = parser().parse_args()
    try:
        repository = Repository(args.source_repo)
        selection = Selection(repository, args.scope)
        if args.validate_only:
            from validate_corpus import validate
            report = validate(selection, args.output, args.snapshot, rebuild=True)
            print(json.dumps(report, indent=2, ensure_ascii=True))
            return 1 if report['status'] == 'fail' else 0
        build = Build(selection)
        print(json.dumps(dict(mode='dry-run' if args.dry_run else 'extract', **build.statistics), indent=2))
        if args.dry_run:
            repository.verify()
            return 0
        build.write(args.output, args.snapshot)
        from validate_corpus import validate
        report = validate(selection, args.output, args.snapshot, rebuild=True)
        print(json.dumps(dict(validation=report['status'], checks=report['checks']), indent=2, ensure_ascii=True))
        return 1 if report['status'] == 'fail' else 0
    except (CorpusError, OSError, ValueError, KeyError, StopIteration) as exc:
        print('Corpus pipeline failed: ' + str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
