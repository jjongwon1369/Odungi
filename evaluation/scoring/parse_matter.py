"""Matter data_model XML → eval/ground_truth/<ver>/records.jsonl

키 = (matter_version, entity, parent_id, id)   (§3.2)

entity 종류
  cluster              parent=None           id=0x0006 (16bit)
                       stub=true: 디바이스 타입만 참조하고 정의 XML이 없는 클러스터
  base_cluster         parent=None           id="base:Mode Base"  (ID 없는 추상 베이스. 이름 존재 확인용)
  attribute            parent=cluster id     id=0x0000 (16bit)
  command              parent=cluster id     id=0x02   (8bit)  commandToServer = AcceptedCommandList
  generated_command    parent=cluster id     id=0x00   (8bit)  commandToClient = GeneratedCommandList
                       (Groups처럼 요청·응답이 같은 ID를 쓰는 경우가 있어 방향을 엔티티로 분리)
  event                parent=cluster id     id=0x00   (8bit)
  feature              parent=cluster id     id="0" (비트 번호), name=코드(LT)
  device_type          parent=None           id=0x0070
  device_type_cluster         parent=device type id  id=cluster id  (server 쪽)
  device_type_client_cluster  parent=device type id  id=cluster id  (client 쪽)
  composed_device_type        parent=device type id  id=구성 device type id   (1.5~)
  composed_cluster_requirement parent="0x0309/0x0510" id=cluster id

파생 클러스터(hierarchy=derived, 예: Refrigerator Alarm ← Alarm Base)는 베이스 요소를 상속하고
파생 XML에 적힌 요소만 덮어쓴다. 상속된 레코드는 inherited_from에 베이스 이름을 남긴다.
베이스 하나가 여러 클러스터 ID를 갖는 경우(Concentration Measurement → 0x040C 등 10개)는
ID마다 전체 레코드를 복제한다.
"""
import argparse, json, pathlib, re, sys
sys.stdout.reconfigure(encoding="utf-8")
import xml.etree.ElementTree as ET
from collections import Counter

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from matter_ids import norm_id, rec_key

ROOT = pathlib.Path(__file__).resolve().parent.parent
DM = ROOT / "data" / "data_model"
GT = ROOT / "eval" / "ground_truth"

CONF_TAGS = {"mandatoryConform", "optionalConform", "provisionalConform", "deprecateConform",
             "disallowConform", "describedConform", "otherwiseConform", "obsoleteConform"}
SIMPLE = {"provisionalConform": "P", "deprecateConform": "D", "disallowConform": "X",
          "describedConform": "desc", "obsoleteConform": "Z"}


# ---------- conformance → 스펙 표기 문자열 ----------
def _term(e):
    t = e.tag
    if t in ("feature", "condition", "attribute", "command", "field", "event"):
        return e.get("name")
    if t in ("literal", "value"):
        return e.get("value")
    if t == "revision":                      # 1.7~: <revision value="current"/> ≥ <revision value="3"/>
        v = e.get("value")
        return "Rev" if v == "current" else v
    if t == "notTerm":
        return "!" + _wrap(e[0])
    if t in ("andTerm", "orTerm"):
        op = " & " if t == "andTerm" else " | "
        return op.join(_wrap(c) for c in e)
    ops = {"greaterTerm": ">", "equalTerm": "==", "lessTerm": "<",
           "greaterOrEqualTerm": ">=", "lessOrEqualTerm": "<="}
    if t in ops and len(e) == 2:
        return f"{_term(e[0])} {ops[t]} {_term(e[1])}"
    if t in CONF_TAGS:
        return _conf_one(e)
    return t


def _wrap(e):
    s = _term(e)
    return f"({s})" if e.tag in ("andTerm", "orTerm") else s


def _conf_one(c):
    if c.tag == "otherwiseConform":
        return ", ".join(_conf_one(k) for k in c)
    if c.tag in SIMPLE:
        return SIMPLE[c.tag]
    expr = " & ".join(_wrap(k) for k in c)
    if c.tag == "mandatoryConform":
        return expr or "M"
    s = f"[{expr}]" if expr else "O"                       # optionalConform
    if c.get("choice"):
        s += "." + c.get("choice") + ("+" if c.get("more") == "true" else "")
    return s


def conformance(el):
    """(표기 문자열, 클래스). 클래스 ∈ M/O/P/D/X/C(조건부)/desc/None"""
    cs = [c for c in el if c.tag in CONF_TAGS]
    if not cs:
        return None, None
    c = cs[0]
    s = _conf_one(c)
    if c.tag == "otherwiseConform":
        cls = "C"
    elif c.tag == "mandatoryConform":
        cls = "M" if len(c) == 0 else "C"
    elif c.tag == "optionalConform":
        cls = "O" if len(c) == 0 else "C"
    else:
        cls = SIMPLE[c.tag] if c.tag != "describedConform" else "desc"
    return s, cls


# ---------- 클러스터 ----------
ELEMS = [  # (컨테이너, 태그, 매칭 키)
    ("features", "feature", "code"),
    ("attributes", "attribute", "id"),
    ("commands", "command", "id"),
    ("events", "event", "id"),
]


def strip_cluster(name):
    return re.sub(r"\s+Clusters?$", "", name or "").strip()


def elem_map(root):
    """루트의 요소들을 {(태그, 매칭키): element} 로. 커맨드는 (id, 방향)까지."""
    out = {}
    for cont, tag, key in ELEMS:
        c = root.find(cont)
        if c is None:
            continue
        for e in c.findall(tag):
            k = e.get(key)
            if k is None:
                continue
            if tag == "command":
                k = (norm_id("command", k), e.get("direction"), e.get("name"))
            elif tag in ("attribute", "event"):
                k = norm_id(tag, k)
            out[(tag, k)] = e
    return out


def merge(base_root, derived_root, base_name):
    """베이스 요소 + 파생 덮어쓰기 → [(element, override_element|None, inherited_from|None)]"""
    bm, dm = elem_map(base_root), elem_map(derived_root)
    used, merged = set(), []
    for (tag, k), be in bm.items():
        de = dm.get((tag, k))
        if de is None and tag == "command":      # 파생 쪽은 direction이 빠진 경우가 있음 → 이름, 그다음 id로
            de_k = next((kk for kk in dm if kk[0] == "command" and kk[1][2] == k[2]), None) \
                or next((kk for kk in dm if kk[0] == "command" and kk[1][0] == k[0] and kk[1][1] is None), None)
            if de_k:
                de = dm[de_k]
                used.add(de_k)
        if de is not None:
            used.add((tag, k))
        merged.append((be, de, None if de is not None else base_name))
    for kk, de in dm.items():
        if kk not in used:
            merged.append((de, None, None))
    return merged


def get(attr, *els):
    for e in els:
        if e is not None and e.get(attr) is not None:
            return e.get(attr)
    return None


def elem_records(ver, cid, merged, src, commit):
    out = []
    for be, de, inh in merged:
        tag = be.tag
        conf_el = de if (de is not None and any(c.tag in CONF_TAGS for c in de)) else be
        conf, cls = conformance(conf_el)
        r = {"matter_version": ver, "parent_id": cid}
        if tag == "feature":
            r.update(entity="feature", id=norm_id("feature", get("bit", de, be)), name=get("code", de, be),
                     label=get("name", de, be))
        elif tag == "command":
            direction = get("direction", be, de)
            r.update(entity="generated_command" if direction == "responseFromServer" or direction == "commandToClient"
                     else "command",
                     id=norm_id("command", get("id", de, be)), name=get("name", de, be),
                     direction=direction, response=get("response", de, be))
        else:
            r.update(entity=tag, id=norm_id(tag, get("id", de, be)), name=get("name", de, be))
            if tag == "attribute":
                r.update(type=get("type", de, be), default=get("default", de, be))
            else:
                r.update(priority=get("priority", de, be))
        r.update(conformance=conf, conf_class=cls, inherited_from=inh, source_file=src, commit=commit)
        out.append({k: v for k, v in r.items() if v is not None or k in ("parent_id", "inherited_from")})
    return out


def parse_version(ver, commit):
    cdir = DM / ver / "clusters"
    roots = {f: ET.parse(f).getroot() for f in sorted(cdir.glob("*.xml"))}

    by_name = {}   # 베이스 탐색용: 이름 → (file, root)
    for f, r in roots.items():
        for n in [strip_cluster(r.get("name"))] + [c.get("name") for c in (r.find("clusterIds") if r.find("clusterIds") is not None else [])]:
            if n:
                by_name.setdefault(n.lower(), (f, r))

    recs = []
    for f, r in roots.items():
        src = f"data_model/{ver}/clusters/{f.name}"
        cl = r.find("classification")
        base_name = cl.get("baseCluster") if cl is not None else None
        if base_name:
            bf, br = by_name[base_name.lower()]
            merged = merge(br, r, base_name)
        else:
            merged = [(e, None, None) for e in elem_map(r).values()]

        cids = r.find("clusterIds")
        ids = [c for c in (cids if cids is not None else []) if c.get("id")]
        if not ids:   # ID 없는 추상 베이스 (Mode Base, Alarm Base, Label)
            recs.append({"matter_version": ver, "entity": "base_cluster", "parent_id": None,
                         "id": f"base:{strip_cluster(r.get('name'))}", "name": strip_cluster(r.get("name")),
                         "revision": r.get("revision"), "inherited_from": None,
                         "source_file": src, "commit": commit})
            continue
        for c in ids:
            cid = norm_id("cluster", c.get("id"))
            recs.append({"matter_version": ver, "entity": "cluster", "parent_id": None, "id": cid,
                         "name": c.get("name"), "revision": r.get("revision"),
                         "hierarchy": cl.get("hierarchy") if cl is not None else None,
                         "base_cluster": base_name, "pics": cl.get("picsCode") if cl is not None else None,
                         "inherited_from": None, "source_file": src, "commit": commit})
            recs.extend(elem_records(ver, cid, merged, src, commit))

    for f in sorted((DM / ver / "device_types").glob("*.xml")):
        r = ET.parse(f).getroot()
        src = f"data_model/{ver}/device_types/{f.name}"
        did = norm_id("device_type", r.get("id"))
        if did is None:          # BaseDeviceType 등 ID 없는 문서
            continue
        cl = r.find("classification")
        recs.append({"matter_version": ver, "entity": "device_type", "parent_id": None, "id": did,
                     "name": r.get("name"), "revision": r.get("revision"),
                     "class": cl.get("class") if cl is not None else None,
                     "superset": cl.get("superset") if cl is not None else None,
                     "inherited_from": None, "source_file": src, "commit": commit})
        for c in r.findall("clusters/cluster"):
            conf, cls = conformance(c)
            side = c.get("side")
            recs.append({"matter_version": ver, "entity": "device_type_cluster" if side == "server"
                         else "device_type_client_cluster", "parent_id": did,
                         "id": norm_id("cluster", c.get("id")), "name": c.get("name"), "side": side,
                         "conformance": conf, "conf_class": cls, "inherited_from": None,
                         "source_file": src, "commit": commit})
        # 1.5~ 조합 디바이스 요구사항 (HeatPump ⊃ Electrical Sensor + Thermostat 등).
        # composedDeviceTypes 바로 아래 <cluster>는 생성기 중복 산출물이라 무시.
        for comp in r.findall("composedDeviceTypes/deviceType"):
            sub = norm_id("device_type", comp.get("deviceTypeId"))
            recs.append({"matter_version": ver, "entity": "composed_device_type", "parent_id": did,
                         "id": sub, "name": comp.get("deviceTypeName"), "inherited_from": None,
                         "source_file": src, "commit": commit})
            for c in comp.findall("clusterRequirements/cluster"):
                conf, cls = conformance(c)
                recs.append({"matter_version": ver, "entity": "composed_cluster_requirement",
                             "parent_id": f"{did}/{sub}", "id": norm_id("cluster", c.get("id")),
                             "name": c.get("name"), "conformance": conf, "conf_class": cls,
                             "inherited_from": None, "source_file": src, "commit": commit})
    # 디바이스 타입이 참조하지만 clusters/에 정의 XML이 없는 클러스터 (예: 1.3 Thermostat → Time 0x000A)
    # → stub 레코드로 남긴다. 없으면 L1이 올바른 답을 "fabricated"로 오판한다.
    defined = {r["id"] for r in recs if r["entity"] == "cluster"}
    stubs = {}
    for r in recs:
        if r["entity"] in ("device_type_cluster", "device_type_client_cluster", "composed_cluster_requirement")                 and r["id"] not in defined and r["id"] not in stubs:
            stubs[r["id"]] = {"matter_version": ver, "entity": "cluster", "parent_id": None, "id": r["id"],
                              "name": r["name"], "stub": True, "inherited_from": None,
                              "source_file": r["source_file"], "commit": commit}
    for sid, st in sorted(stubs.items()):
        print(f"  [{ver}] stub cluster {sid} {st['name']}  (참조: {st['source_file']})")
    return recs + list(stubs.values())


def main():
    global DM
    ap = argparse.ArgumentParser()
    ap.add_argument("--versions", nargs="+", default=["1.3", "1.4", "1.5"])
    ap.add_argument("--data-root", type=pathlib.Path, default=DM, help="XML snapshot directory containing SOURCE.json")
    a = ap.parse_args()
    DM = a.data_root
    commit = json.loads((DM / "SOURCE.json").read_text())["commit"]

    for ver in a.versions:
        recs = parse_version(ver, commit)
        # 원본 XML 자체의 동일 중복 행(BatteryStorage 1.5 등)은 하나로 합침
        seen, uniq, same_dup = {}, [], []
        for r in recs:
            k = rec_key(r)
            if k in seen and seen[k] == r:
                same_dup.append(k)
                continue
            seen.setdefault(k, r)
            uniq.append(r)
        recs = uniq
        for k in same_dup:
            print(f"  [{ver}] 원본 중복 행 병합: {k}")
        # 키 유일성 검사 — 내용이 다른 중복이면 스키마가 틀린 것
        dup = [k for k, n in Counter(rec_key(r) for r in recs).items() if n > 1]
        if dup:
            for k in dup[:10]:
                print("  DUP", k, [ (r["name"], r["source_file"]) for r in recs if rec_key(r) == k])
            sys.exit(f"{ver}: 키 중복 {len(dup)}건")
        recs.sort(key=lambda r: tuple(str(x) for x in rec_key(r)))
        out = GT / ver / "records.jsonl"
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("w", encoding="utf-8") as fp:
            for r in recs:
                fp.write(json.dumps(r, ensure_ascii=False) + "\n")
        cnt = Counter(r["entity"] for r in recs)
        print(f"[{ver}] {len(recs):>5} records  " + "  ".join(f"{k}={v}" for k, v in sorted(cnt.items())))


if __name__ == "__main__":
    main()
