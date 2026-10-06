"""Identifier values and preferred display format are separate.
WIDTH controls canonical spelling only; it is not a Matter bit-width definition.
"""
import re

WIDTH = {"cluster": 4, "base_cluster": None, "attribute": 4, "device_type": 4,
         "device_type_cluster": 4, "device_type_client_cluster": 4,
         "composed_device_type": 4, "composed_cluster_requirement": 4,
         "command": 2, "generated_command": 2, "event": 2}

HEX_RE = re.compile(r"^0[xX]([0-9a-fA-F]{1,8})$")


def norm_id(entity, raw):
    """XML/답변의 원 문자열을 엔티티 폭에 맞춘 대문자 hex로. 실패하면 None."""
    if raw is None:
        return None
    raw = str(raw).strip()
    if entity == "feature":
        return str(int(raw, 16 if raw.lower().startswith("0x") else 10)) if re.fullmatch(r"0[xX][0-9a-fA-F]+|[0-9]+", raw) else None
    m = HEX_RE.match(raw)
    if not m:
        return None
    v = int(m.group(1), 16)
    w = WIDTH.get(entity)
    if w is None:
        return None
    if w == 2 and v > 0xFF:          # 8비트 초과 커맨드/이벤트는 그대로 4자리 유지
        w = 4
    return f"0x{v:0{w}X}"


def width_ok(entity, raw):
    """Preferred display width only; failure must not remove semantic credit."""
    m = HEX_RE.match(raw.strip())
    if not m:
        return False
    w = WIDTH.get(entity)
    return w is None or len(m.group(1)) == w or (w == 2 and int(m.group(1), 16) > 0xFF and len(m.group(1)) == 4)


def norm_name(name):
    """이름 비교용 키: 대소문자·공백·기호 무시, 끝의 'Cluster'/'Attribute'/'Command' 제거.
    'On/Off Cluster' == 'OnOff' == 'on off'"""
    if name is None:
        return None
    s = re.sub(r"\s+(cluster|clusters|attribute|command|event|device type)$", "", name.strip(), flags=re.I)
    return re.sub(r"[^0-9a-z]", "", s.lower())


def rec_key(r):
    return (r["matter_version"], r["entity"], r["parent_id"], r["id"])
