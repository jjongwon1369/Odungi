"""Lossless source excerpts, not summaries or retrieval chunks.

Offsets address Unicode code points in the UTF-8-decoded, LF-normalized source.
Every output character except the separator LF belongs to a recorded span.
"""
from __future__ import annotations

from collections import Counter
import json
import re
import xml.parsers.expat
from corpus_utils import canonical_text, digest, canonical, require


def number(value):
    if isinstance(value, int):
        return value
    s = str(value).strip()
    return int(s, 16 if s.lower().startswith('0x') else 10)


def inventory(text):
    # Includes IDs, enum members, XML/IDL names and C/C++ identifiers verbatim.
    return Counter(re.findall(r'0[xX][0-9a-fA-F]+|[A-Za-z_][A-Za-z_0-9]*|[0-9]+', text))


def xml_tree(text):
    offsets = {}
    byte = 0
    for index, char in enumerate(text):
        offsets[byte] = index
        byte += len(char.encode('utf-8'))
    offsets[byte] = len(text)
    parser = xml.parsers.expat.ParserCreate()
    stack, roots = [], []

    def start(name, attrs):
        pos = offsets[parser.CurrentByteIndex]
        # XML attribute values can contain >; honor quotes.
        match = re.match(r'<(?:[^>\"\']|\"[^\"]*\"|\'[^\']*\')*>', text[pos:])
        require(match is not None, 'Cannot locate XML opening tag')
        end = pos + match.end()
        node = dict(name=name, attrs=attrs, start=pos, open_end=end,
                    children=[], self_closing=text[pos:end].rstrip().endswith('/>'))
        (stack[-1]['children'] if stack else roots).append(node)
        stack.append(node)

    def end(name):
        node = stack.pop()
        node['close_start'] = offsets[parser.CurrentByteIndex] if not node['self_closing'] else node['open_end']
        node['end'] = (text.index('>', node['close_start']) + 1
                       if not node['self_closing'] else node['open_end'])

    parser.StartElementHandler, parser.EndElementHandler = start, end
    parser.ExternalEntityRefHandler = lambda *args: 0
    parser.Parse(text.encode('utf-8'), True)
    require(len(roots) == 1, 'Expected one XML root')
    return roots[0]


def descendants(node, name=None):
    for child in node['children']:
        if name is None or child['name'] == name:
            yield child
        yield from descendants(child, name)


def child_value(node, name, text):
    found = next((c for c in node['children'] if c['name'] == name), None)
    return text[found['open_end']:found['close_start']].strip() if found else None


def subtract(length, removed):
    result, cursor = [], 0
    for a, b in sorted(removed):
        if a > cursor:
            result.append((cursor, a, 'source excerpt'))
        cursor = max(cursor, b)
    if cursor < length:
        result.append((cursor, length, 'source excerpt'))
    return result


def xml_ranges(text, path, selection):
    root = xml_tree(text)
    removed = []
    drop = lambda n: removed.append((n['start'], n['end']))
    if path.endswith('RootNodeDeviceType.xml'):
        for node in root['children']:
            if node['name'] not in {'revisionHistory', 'classification', 'conditions'}:
                drop(node)
            elif node['name'] == 'conditions':
                for condition in node['children']:
                    if condition['attrs'].get('name') != 'GroupcastListenerCond':
                        drop(condition)
    elif root['name'] == 'deviceType':
        pid = next((pid for pid, p in selection.products.items() if p['definition_path'] == path), None)
        if pid is not None:
            for group in root['children']:
                if group['name'] == 'clusters':
                    for node in group['children']:
                        if 'id' in node['attrs'] and number(node['attrs']['id']) not in selection.allowed_for_device(pid):
                            drop(node)
    elif root['name'] == 'configurator' and path.endswith('matter-devices.xml'):
        # Match names through the selected SDK definitions, not guessed display names.
        names = {}
        for c in selection.clusters.values():
            sdk = c['sdk_definition_path']
            if sdk in selection.files:
                sdk_text = canonical_text(selection.repo.read(sdk))
                for n in xml_tree(sdk_text)['children']:
                    code = child_value(n, 'code', sdk_text)
                    if n['name'] == 'cluster' and code:
                        names[number(code)] = child_value(n, 'name', sdk_text)
            # A Device Type include can exist without a concrete SDK Cluster
            # definition (Temperature Alarm). Preserve that explicit reference.
            spec_text = canonical_text(selection.repo.read(c['specification_path']))
            for n in descendants(xml_tree(spec_text), 'clusterId'):
                if number(n['attrs'].get('id', '-1')) == number(c['cluster_id']):
                    names.setdefault(number(c['cluster_id']), n['attrs']['name'])
        for node in root['children']:
            if node['name'] != 'deviceType':
                continue
            value = child_value(node, 'deviceId', text)
            pid = number(value) if value else None
            if pid not in selection.products:
                drop(node)
                continue
            allowed = {names[c] for c in selection.allowed_for_device(pid) if c in names}
            for inc in descendants(node, 'include'):
                if inc['attrs'].get('cluster') not in allowed:
                    drop(inc)
    elif root['name'] == 'configurator':
        for node in root['children']:
            code = child_value(node, 'code', text)
            if node['name'] == 'cluster' and code and number(code) not in selection.clusters:
                drop(node)
                continue
            refs = [n for n in node['children'] if n['name'] == 'cluster' and 'code' in n['attrs']]
            if refs and not any(number(n['attrs']['code']) in selection.clusters for n in refs):
                drop(node)
            else:
                for ref in refs:
                    if number(ref['attrs']['code']) not in selection.clusters:
                        drop(ref)
    elif root['name'] == 'cluster':
        for group in root['children']:
            if group['name'] == 'clusterIds':
                for node in group['children']:
                    value = node['attrs'].get('id')
                    if value and number(value) not in selection.clusters:
                        drop(node)
    return subtract(len(text), removed)


def json_tree(text):
    decoder = json.JSONDecoder()

    def parse(pos):
        while text[pos].isspace():
            pos += 1
        start, children = pos, []
        if text[pos] in '[{':
            is_object = text[pos] == '{'
            closing = '}' if is_object else ']'
            pos += 1
            while True:
                while text[pos].isspace() or text[pos] == ',':
                    pos += 1
                if text[pos] == closing:
                    pos += 1
                    break
                member_start, key = pos, len(children)
                if is_object:
                    key, pos = decoder.raw_decode(text, pos)
                    while text[pos].isspace():
                        pos += 1
                    require(text[pos] == ':', 'Invalid JSON member')
                    pos += 1
                node, pos = parse(pos)
                node.update(key=key, member_start=member_start)
                children.append(node)
            value = {n['key']: n['value'] for n in children} if is_object else [n['value'] for n in children]
        else:
            value, pos = decoder.raw_decode(text, pos)
        return dict(start=start, end=pos, value=value, children=children), pos

    root, end = parse(0)
    require(not text[end:].strip(), 'Trailing JSON data')
    return root


def zap_ranges(text, path, selection):
    root = json_tree(text)
    members = {n['key']: n for n in root['children']}
    ranges, selected_indices = [], set()
    generic = '/all-clusters-app/' in path
    for node in root['children']:
        if node['key'] not in {'endpointTypes', 'endpoints'}:
            ranges.append((node['member_start'], node['end'], '$.' + node['key']))
    for i, endpoint in enumerate(members['endpointTypes']['children']):
        value = endpoint['value']
        pids = {number(v) for v in value.get('deviceIdentifiers', [])} & set(selection.products)
        if not pids and not generic:
            continue
        selected_indices.add(i)
        allowed = set(selection.clusters) if generic else set().union(*(selection.allowed_for_device(p) for p in pids))
        for node in endpoint['children']:
            prefix = f'$.endpointTypes[{i}].{node["key"]}'
            if node['key'] == 'clusters':
                for j, cluster in enumerate(node['children']):
                    if number(cluster['value']['code']) in allowed:
                        ranges.append((cluster['start'], cluster['end'], prefix + f'[{j}]'))
            elif pids or node['key'] in {'name', 'id'}:
                ranges.append((node['member_start'], node['end'], prefix))
    for i, node in enumerate(members.get('endpoints', {}).get('children', [])):
        if node['value'].get('endpointTypeIndex') in selected_indices or node['value'].get('endpointId') == 0:
            ranges.append((node['start'], node['end'], f'$.endpoints[{i}]'))
    require(selected_indices, f'No selected ZAP endpoints in {path}')
    return sorted(ranges)


def mask_comments(text):
    return re.sub(r'//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"',
                  lambda m: ''.join('\n' if c == '\n' else ' ' for c in m[0]), text)


def idl_ranges(text, path, selection):
    masked = mask_comments(text)
    blocks, depth, begin = [], 0, 0
    for i, char in enumerate(masked):
        if char == '{':
            if depth == 0:
                start = begin
                while start < i and masked[start].isspace():
                    start += 1
                opening = i
            depth += 1
        elif char == '}':
            depth -= 1
            require(depth >= 0, f'Unbalanced IDL {path}')
            if depth == 0:
                blocks.append((start, opening, i + 1, masked[start:opening].strip()))
                begin = i + 1
    require(depth == 0, f'Unbalanced IDL {path}')
    ranges, globals_ = [], {}
    names = {}
    for a, op, b, header in blocks:
        m = re.search(r'\bcluster\s+(\w+)\s*=\s*(0x[0-9A-Fa-f]+|\d+)', header)
        if m:
            names[m[1]] = number(m[2])
            if number(m[2]) in selection.clusters:
                ranges.append((a, b, 'cluster ' + m[1]))
        elif re.match(r'(enum|bitmap|struct)\b', header):
            globals_[header.split()[1]] = (a, b, header)
    for a, op, b, header in blocks:
        if not re.match(r'endpoint\s+\d+', header):
            continue
        body = masked[op + 1:b - 1]
        devices = list(re.finditer(r'device\s+type\s+\w+\s*=\s*(0x[0-9a-fA-F]+|\d+)[^;]*;', body))
        pids = {number(m[1]) for m in devices} & set(selection.products)
        if not pids:
            if header == 'endpoint 0':
                ranges.append((a, op + 1, 'root topology context'))
                for m in devices:
                    ranges.append((op + 1 + m.start(), op + 1 + m.end(), 'root device context'))
                ranges.append((b - 1, b, 'root topology end'))
            continue
        allowed = set().union(*(selection.allowed_for_device(p) for p in pids))
        ranges.append((a, op + 1, header))
        for m in devices:
            if number(m[1]) in pids:
                ranges.append((op + 1 + m.start(), op + 1 + m.end(), header + '/device type'))
        for m in re.finditer(r'(?:server|client)\s+cluster\s+(\w+)\s*\{', body):
            if names.get(m[1]) not in allowed:
                continue
            start = op + 1 + m.start()
            cursor, nested = op + 1 + m.end(), 1
            while nested and cursor < b:
                nested += (masked[cursor] == '{') - (masked[cursor] == '}')
                cursor += 1
            require(nested == 0, 'Unbalanced endpoint cluster')
            ranges.append((start, cursor, header + '/cluster ' + m[1]))
        ranges.append((b - 1, b, header + '/end'))
    # Only referenced same-file global types; no external dependency traversal.
    while True:
        identifiers = inventory('\n'.join(text[a:b] for a, b, _ in ranges))
        wanted = set(globals_) & identifiers.keys()
        if not wanted:
            break
        ranges.extend(globals_.pop(name) for name in sorted(wanted))
    require(ranges, f'No scoped IDL definitions in {path}')
    # Preserve generated header comments as provenance.
    if blocks and blocks[0][0] > 0:
        ranges.append((0, blocks[0][0], 'generated header'))
    return sorted(ranges)


def selected_ranges(text, path, selection):
    if path.endswith('.xml'):
        return xml_ranges(text, path, selection)
    if path.endswith('.zap'):
        return zap_ranges(text, path, selection)
    if path.endswith('.matter'):
        return idl_ranges(text, path, selection)
    if path.endswith('/CMakeLists.txt'):
        ranges, offset = [], 0
        for line in text.splitlines(keepends=True):
            if any(n in line for n in ['target_sources(', 'target_include_directories(',
                                      'laundry-washer-mode.cpp', 'DeviceCallbacks.cpp', 'ZclCallbacks.cpp',
                                      'laundry-washer-controls-delegate-impl.cpp',
                                      '${ALL_CLUSTERS_COMMON_DIR}/include', '${NXP_EXAMPLE_DIR}/main/include']):
                ranges.append((offset, offset + len(line), 'allowlisted build evidence'))
            offset += len(line)
        require(ranges, 'Missing allowlisted build evidence')
        return ranges
    return [(0, len(text), 'complete allowed file')]


def normalize(path, data, selection):
    text = canonical_text(data)
    ranges = selected_ranges(text, path, selection)
    spans, parts, previous = [], [], 0
    for a, b, locator in ranges:
        require(0 <= a < b <= len(text) and a >= previous, f'Invalid/overlapping span: {path}')
        previous = b
        parts.append(text[a:b])
        spans.append(dict(source_path=path, char_start=a, char_end=b,
                          line_start=text.count('\n', 0, a) + 1,
                          line_end=text.count('\n', 0, b - 1) + 1, locator=locator))
    result = '\n'.join(parts)
    require(bool(result.strip()), f'Empty normalized file: {path}')
    return dict(text=result, source_spans=spans, normalized_hash=digest(result.encode('utf-8')),
                identifier_inventory=dict(sorted(inventory(result).items())))
