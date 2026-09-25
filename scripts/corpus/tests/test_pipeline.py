"""Local integration tests. The reference checkout is never modified."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from corpus_utils import (CorpusError, PROJECT_ROOT, Repository, Selection,
                          csv_bytes, digest, document_id, relation_semantic_key,
                          writable_path)
from compare_tiers import spans_preserved
from extract_corpus import Build
from generate_scope import build_draft, resolve_device_types
from normalize_corpus import normalize, xml_tree
from validate_corpus import rebuild_check, unique_ids, validate, verify_hash


class PipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo = Repository(PROJECT_ROOT.parent / 'connectedhomeip')
        cls.scope = PROJECT_ROOT / 'corpus/metadata/scope.json'
        cls.selection = Selection(cls.repo, cls.scope)
        cls.build = Build(cls.selection)

    def test_wrong_commit_fails_before_remote_or_checkout(self):
        with patch.object(Repository, 'git', return_value=b'0' * 40 + b'\n') as git:
            with self.assertRaisesRegex(CorpusError, 'Commit mismatch'):
                Repository(self.repo.root)
            self.assertEqual(git.call_args_list[0].args, ('rev-parse', 'HEAD'))
            self.assertEqual(git.call_count, 1)

    def test_dirty_source_rejected(self):
        original = self.repo.git
        def git(*args):
            return b' M tracked-file\n' if args[0] == 'status' else original(*args)
        with patch.object(self.repo, 'git', side_effect=git):
            with self.assertRaisesRegex(CorpusError, 'dirty'):
                self.repo.verify()

    def test_nonexistent_source_file(self):
        with self.assertRaisesRegex(CorpusError, 'absent from pinned commit'):
            self.repo.read('data_model/1.7/clusters/DoesNotExist.xml')

    def test_duplicate_document_id(self):
        row = self.build.manifest[0]
        with self.assertRaisesRegex(CorpusError, 'Duplicate document_id'):
            unique_ids([row, row], 'document_id')

    def test_hash_mismatch(self):
        with self.assertRaisesRegex(CorpusError, 'Hash mismatch'):
            verify_hash(b'changed', digest(b'original'), 'fixture')

    def test_tier_span_preservation_allows_merged_superset(self):
        lower = [
            {'source_path': 'source.xml', 'char_start': 0, 'char_end': 10},
            {'source_path': 'source.xml', 'char_start': 12, 'char_end': 20},
        ]
        upper = [{'source_path': 'source.xml', 'char_start': 0, 'char_end': 25}]
        self.assertTrue(spans_preserved(lower, upper))
        self.assertFalse(spans_preserved(lower, [
            {'source_path': 'source.xml', 'char_start': 0, 'char_end': 19},
        ]))

    def test_shared_implementation_one_file_many_devices(self):
        path = 'src/app/clusters/mode-base-server/ModeBaseCluster.cpp'
        records = [r for r in self.build.manifest if r['source_path'] == path]
        self.assertEqual(len(records), 1)
        self.assertEqual(set(records[0]['device_types']), {'0x0070', '0x0071', '0x0072', '0x0073'})
        relations = [r for r in self.build.relations if r['document_id'] == document_id(path)
                     and r['relation_type'] == 'uses_shared_implementation']
        self.assertEqual(len(relations), 4)
        self.assertEqual(len({json.dumps(r['target_entity'], sort_keys=True) for r in relations}), 1)

    def test_normalization_preserves_utf8_newlines_and_identifiers(self):
        raw = b'\xef\xbb\xbf// caf\xc3\xa9\r\nclass Mode_0x0073 {};\rnext();\n'
        doc = normalize('fixture.cpp', raw, self.selection)
        self.assertEqual(doc['text'], '// caf\u00e9\nclass Mode_0x0073 {};\nnext();\n')
        self.assertEqual(doc['source_spans'][0]['line_end'], 3)
        self.assertIn('Mode_0x0073', doc['identifier_inventory'])
        tree = xml_tree('<root a="x>y"><item name="\u00e9"/></root>')
        self.assertEqual(tree['end'], len('<root a="x>y"><item name="\u00e9"/></root>'))

    def test_scope_slicing_excludes_heater_and_other_resource(self):
        path = 'data_model/1.7/device_types/TemperatureControlledCabinet.xml'
        text = normalize(path, self.repo.read(path), self.selection)['text']
        self.assertNotIn('<cluster id="0x0048"', text)
        self.assertNotIn('<cluster id="0x0049"', text)
        self.assertIn('<cluster id="0x0064"', text)
        path = 'data_model/1.7/clusters/ResourceMonitoring.xml'
        text = normalize(path, self.repo.read(path), self.selection)['text']
        self.assertNotIn('<clusterId id="0x0079"', text)
        self.assertIn('<clusterId id="0x0071"', text)
        path = 'src/app/zap-templates/zcl/data-model/chip/matter-devices.xml'
        text = normalize(path, self.repo.read(path), self.selection)['text']
        self.assertIn('include cluster="Temperature Alarm"', text)

    def test_identifier_corruption_and_raw_corruption_detected(self):
        with tempfile.TemporaryDirectory(prefix='.corpus-test-', dir=PROJECT_ROOT) as directory:
            root = writable_path(directory, self.repo.root)
            self.build.write(root / 'raw', root / 'metadata/snapshot.json')
            docfile = root / 'processed/documents.jsonl'
            docs = [json.loads(line) for line in docfile.read_text(encoding='utf-8').splitlines()]
            docs[0]['text'] += '\nIdentifier_WAS_CHANGED\n'
            docfile.write_text(''.join(json.dumps(d) + '\n' for d in docs), encoding='utf-8')
            raw = root / self.build.manifest[0]['raw_path']
            raw.write_bytes(raw.read_bytes() + b'changed')
            manifest = copy.deepcopy(self.build.manifest)
            manifest.append(manifest[0])
            (root / 'metadata/corpus_manifest.csv').write_bytes(csv_bytes(manifest))
            report = validate(self.selection, root / 'raw', root / 'metadata/snapshot.json', rebuild=False, write_report=False)
            for key in ['duplicate_document_id', 'manifest_raw_consistency_and_hash_validity',
                        'source_span_validity', 'identifier_preservation', 'coverage_matrix_consistency']:
                self.assertEqual(report['checks'][key]['status'], 'fail', key)

    def test_deterministic_rebuild(self):
        result = rebuild_check(self.selection)
        self.assertEqual(result['builds'], 2)
        self.assertEqual(result['relations'], 'identical')

    def test_source_and_output_guards(self):
        with self.assertRaises(CorpusError):
            writable_path(self.repo.root / 'should-not-be-created', self.repo.root)
        with self.assertRaises(CorpusError):
            self.repo.check_file('../outside.cpp')

    def test_document_id_is_path_based(self):
        path = 'src/app/clusters/mode-base-server/ModeBaseCluster.cpp'
        self.assertEqual(document_id(path), document_id(path))
        self.assertNotEqual(document_id(path), document_id(path + '.other'))
        self.assertNotEqual(document_id(path).split(':')[1], digest(self.repo.read(path)))

    def test_each_source_keeps_its_own_revision(self):
        rows = {r['source_path']: r for r in self.build.manifest}
        for cid, cluster in self.selection.clusters.items():
            for field, key in [('specification_path', 'specification_revision'), ('sdk_definition_path', 'sdk_revision')]:
                if cluster[field] not in rows:
                    continue
                declarations = rows[cluster[field]]['source_revision']['declarations']
                self.assertEqual({d['value'] for d in declarations
                                  if d['entity_kind'] == 'cluster' and d['entity_id'] == f'0x{cid:04X}'}, {cluster[key]})
        requirements = {r['requirement'] for r in self.build.relations}
        self.assertTrue(requirements <= {None, 'mandatory', 'optional', 'conditional', 'provisional', 'disallowed', 'not_applicable'})

    def test_relation_semantic_key_is_canonical_and_ignores_tier_metadata(self):
        relation = copy.deepcopy(self.build.relations[0])
        key = relation_semantic_key(relation)
        changed = copy.deepcopy(relation)
        changed['relation_id'] = 'rel:changed'
        changed['via_entities'] = [{'kind': 'cluster', 'id': '0xFFFF'}]
        self.assertEqual(key, relation_semantic_key(changed))
        changed['requirement'] = 'optional' if relation.get('requirement') != 'optional' else 'mandatory'
        self.assertNotEqual(key, relation_semantic_key(changed))

    def test_tier_declarations_are_nested_and_generate_review_only_drafts(self):
        c3 = resolve_device_types('c3')
        c6 = resolve_device_types('c6')
        c12 = resolve_device_types('c12')
        self.assertEqual(len(c3), 4)
        self.assertEqual(len(c6), 7)
        self.assertEqual(len(c12), 14)
        self.assertLess(set(c3), set(c6))
        self.assertLess(set(c6), set(c12))
        draft = build_draft(self.repo, 'c3')
        self.assertTrue(draft['draft'])
        self.assertFalse(draft['extraction_authorized'])
        self.assertEqual(draft['repository']['commit_sha'], self.repo.head)
        self.assertEqual(draft['counts']['product_families'], 3)
        self.assertEqual({item['id'] for item in draft['products']},
                         {'0x0070', '0x0071', '0x0072', '0x0073'})
        existing = {item['id']: item for item in self.selection.scope['products']}
        for product in draft['products']:
            baseline = existing[product['id']]
            for field in ['name', 'definition_path', 'direct_cluster_ids', 'base_cluster_ids', 'product_role']:
                self.assertEqual(product[field], baseline[field], (product['id'], field))


if __name__ == '__main__':
    unittest.main()
