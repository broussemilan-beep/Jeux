"""
Lecteur du format binaire .rbxm/.rbxl (chunks META/SSTR/INST/PROP/PRNT/END,
LZ4 raw block par chunk) -- pas une lib complete, juste assez pour
inventorier un pack Roblox (rig, VFX, animations) et en extraire les
donnees numeriques utiles (rotations de Pose, courbes de particules) sans
deviner a l'oeil sur un dump brut illisible.

Base sur le format documente par rbx-dom (reverse-engineered, verifie par
la communaute). Ecrit et VALIDE contre des fichiers reels le 2026-09-03
(voir experiments/_shared/README.md pour la methode de validation et les
limites connues) -- chaque hypothese de layout ci-dessous a ete confirmee
empiriquement (matrices de rotation orthonormales, LocalScript.Source
retrouve caractere pour caractere identique au script Animate.lua
standard de Roblox, valeurs par defaut plausibles comme MaxHealth=100),
jamais juste "ca a l'air de marcher".

Limite connue et non resolue : pour les tres grands tableaux Vector3/
CFrame (plusieurs milliers d'instances, ex. Pose.CFrame dans un pack
d'animation), le POSITION (pas la rotation, qui reste parfaitement
validee) contient une fraction significative (~15-35%) de valeurs
manifestement fausses (magnitudes absurdes) -- cause exacte non
identifiee (le decompte d'octets total est exact au byte pres, donc ce
n'est pas un desalignement). A traiter comme non fiable pour l'instant ;
filtrer par plausibilite (|valeur| > ~50 studs = suspect) si utilise.
"""
import struct
import sys

import lz4.block

try:
    import numpy as np
except ImportError:
    np = None


# ---------------------------------------------------------------------
# Chunks

def read_chunks(path):
    with open(path, "rb") as f:
        data = f.read()
    assert data[0:8] == b"<roblox!", "pas un fichier rbxm/rbxl binaire (magic absent)"
    assert data[8:14] == b"\x89\xff\x0d\x0a\x1a\x0a", "signature binaire absente"
    version, num_types, num_instances = struct.unpack_from("<HII", data, 14)
    pos = 32
    chunks = []
    while pos < len(data):
        tag = data[pos:pos + 4].rstrip(b"\x00").decode("ascii")
        comp_len, uncomp_len, _reserved = struct.unpack_from("<III", data, pos + 4)
        pos += 16
        raw = data[pos:pos + comp_len] if comp_len else data[pos:pos + uncomp_len]
        pos += comp_len if comp_len else uncomp_len
        payload = lz4.block.decompress(raw, uncompressed_size=uncomp_len) if comp_len else raw
        chunks.append((tag, payload))
        if tag == "END":
            break
    return version, num_types, num_instances, chunks


def read_string(buf, off):
    (n,) = struct.unpack_from("<I", buf, off)
    off += 4
    return buf[off:off + n], off + n


# ---------------------------------------------------------------------
# Tableaux numeriques transposes (positions, floats scalaires, entiers,
# referents) : stockes "colonne par colonne" (tous les octets 0 de chaque
# valeur, puis tous les octets 1, ...) -- une astuce de compression
# Roblox pour que LZ4 trouve plus de redondance.

def untranspose_interleave(buf, count, width):
    out = bytearray(count * width)
    for col in range(width):
        base = col * count
        for i in range(count):
            out[i * width + col] = buf[base + i]
    return bytes(out)


def zigzag_decode(u):
    return (u >> 1) ^ (-(u & 1))


def decode_int32_array(buf, count):
    raw = untranspose_interleave(buf, count, 4)
    return [zigzag_decode(v) for v in struct.unpack(f">{count}I", raw)]


def decode_referents(buf, count):
    """Tableau d'ID d'instance (INST, ou parent/enfant de PRNT) : meme
    transposition+zigzag que decode_int32_array, PUIS cumsum (delta-encode
    croissant)."""
    acc = 0
    out = []
    for d in decode_int32_array(buf, count):
        acc += d
        out.append(acc)
    return out


def decode_float32_array(buf, count):
    """Les flottants passent par le MEME pipeline que les entiers, mais le
    resultat est une REINTERPRETATION DES BITS en IEEE754, pas une
    conversion de valeur -- verifie empiriquement : Humanoid.MaxHealth (1
    flottant, octets bruts 0x85900000) zigzag-decode (sans cumsum) vers
    l'entier 1120133120 = 0x42C80000 en bits = 100.0f pile (valeur par
    defaut plausible)."""
    return [struct.unpack("<f", struct.pack("<i", v))[0]
            for v in decode_int32_array(buf, count)]


# ---------------------------------------------------------------------
# INST / PROP (types simples)

def parse_inst_chunks(chunks):
    """class_id -> {"name", "is_service", "referents":[...]}"""
    classes = {}
    for tag, payload in chunks:
        if tag != "INST":
            continue
        off = 0
        (class_id,) = struct.unpack_from("<I", payload, off); off += 4
        name_bytes, off = read_string(payload, off)
        is_service = payload[off]; off += 1
        (n,) = struct.unpack_from("<I", payload, off); off += 4
        referents = decode_referents(payload[off:], n)
        classes[class_id] = {"name": name_bytes.decode("utf-8", "replace"),
                              "is_service": bool(is_service), "referents": referents}
    return classes


def ref_class_map(classes):
    """referent -> class_name, pour tout le fichier."""
    out = {}
    for c in classes.values():
        for r in c["referents"]:
            out[r] = c["name"]
    return out


def parse_prop_chunks(chunks, classes):
    """[(class_name, prop_name, dtype, {referent: valeur})] -- uniquement
    String(1)/Bool(2)/Int32(3)/Float32(4). Autres types : valeurs =
    {"_raw_len":..., "_dtype":...} (voir parse_prop_extended pour
    CFrame/NumberSequence/ColorSequence/NumberRange)."""
    results = []
    for tag, payload in chunks:
        if tag != "PROP":
            continue
        off = 0
        (class_id,) = struct.unpack_from("<I", payload, off); off += 4
        prop_bytes, off = read_string(payload, off)
        dtype = payload[off]; off += 1
        cls = classes.get(class_id)
        if cls is None:
            continue
        refs = cls["referents"]
        n = len(refs)
        body = payload[off:]
        values = {}
        try:
            if dtype == 0x01:  # String
                p = 0
                for r in refs:
                    s, p = read_string(body, p)
                    values[r] = s.decode("utf-8", "replace")
            elif dtype == 0x02:  # Bool
                for i, r in enumerate(refs):
                    values[r] = bool(body[i])
            elif dtype == 0x03:  # Int32
                for r, v in zip(refs, decode_int32_array(body, n)):
                    values[r] = v
            elif dtype == 0x04:  # Float32
                for r, v in zip(refs, decode_float32_array(body, n)):
                    values[r] = v
            else:
                values = {"_raw_len": len(body), "_dtype": dtype}
        except Exception as e:
            values = {"_error": str(e), "_raw_len": len(body), "_dtype": dtype}
        results.append((cls["name"], prop_bytes.decode("utf-8", "replace"), dtype, values))
    return results


# ---------------------------------------------------------------------
# PRNT (hierarchie parent/enfant)

def parse_prnt_chunk(chunks):
    """referent_enfant -> referent_parent (absent si racine)."""
    for tag, payload in chunks:
        if tag != "PRNT":
            continue
        (num_links,) = struct.unpack_from("<I", payload, 1)
        off = 5
        children = decode_referents(payload[off:off + num_links * 4], num_links); off += num_links * 4
        parents = decode_referents(payload[off:off + num_links * 4], num_links)
        return dict(zip(children, parents))
    return {}


def find_ancestor_of_class(ref, parent_of, ref_class, target_class, max_depth=20):
    seen = 0
    while ref in parent_of and seen < max_depth:
        ref = parent_of[ref]
        seen += 1
        if ref_class.get(ref) == target_class:
            return ref
    return None


# ---------------------------------------------------------------------
# Types "riches" : CFrame(16), NumberSequence(21), ColorSequence(22),
# NumberRange(23). A la demande (want = {(class,prop): kind}) car plus
# couteux et pas toujours utiles.

def decode_cframe_array(buf, n):
    """[(pos(x,y,z), rot3x3_ou_None, rot_id)]. rot_id==0 => matrice brute
    (9 flottants LITTLE-endian sequentiels -- PAS le pipeline transpose+
    zigzag des tableaux, verifie empiriquement : orthonormalite ~4e-08
    avec ce layout contre ~1e51/garbage avec big-endian ou le bit-trick
    zigzag). rot_id!=0 => rotation "speciale" (axes alignes, table de
    correspondance NON geree ici -- rencontree seulement pour des
    rotations identite dans les fichiers testes, ex. HumanoidRootPart)."""
    off = 0
    rot_ids, raw_mats = [], []
    for _ in range(n):
        rid = buf[off]; off += 1
        rot_ids.append(rid)
        if rid == 0:
            raw_mats.append(struct.unpack_from("<9f", buf, off))
            off += 36
        else:
            raw_mats.append(None)
    xs = decode_float32_array(buf[off:], n); off += n * 4
    ys = decode_float32_array(buf[off:], n); off += n * 4
    zs = decode_float32_array(buf[off:], n); off += n * 4
    return [((xs[i], ys[i], zs[i]), raw_mats[i], rot_ids[i]) for i in range(n)], off


def rotation_angle_deg(mat9):
    """Angle (deg) entre la matrice 3x3 (9 floats row-major) et l'identite
    -- angle de l'axe-angle equivalent, via trace(M). Independant de la
    convention d'axes (contrairement a une decomposition en Euler XYZ),
    utile pour comparer objectivement des amplitudes de pose entre deux
    rigs/conventions differentes."""
    if np is None:
        raise RuntimeError("numpy requis pour rotation_angle_deg")
    M = np.array(mat9).reshape(3, 3)
    tr = np.clip((np.trace(M) - 1) / 2, -1, 1)
    return float(np.degrees(np.arccos(tr)))


def decode_numbersequence_array(buf, n):
    """NumberSequence : [count:u32][(time,value,envelope) x count] par
    instance, flottants BIG-endian sequentiels (pas transposes -- taille
    variable par instance, la transposition ne s'applique pas)."""
    off = 0
    out = []
    for _ in range(n):
        (cnt,) = struct.unpack_from(">I", buf, off); off += 4
        kps = []
        for _k in range(cnt):
            t, v, env = struct.unpack_from(">3f", buf, off); off += 12
            kps.append((t, v, env))
        out.append(kps)
    return out, off


def decode_colorsequence_array(buf, n):
    """ColorSequence : [count:u32][(time,r,g,b,envelope) x count]."""
    off = 0
    out = []
    for _ in range(n):
        (cnt,) = struct.unpack_from(">I", buf, off); off += 4
        kps = []
        for _k in range(cnt):
            t, r, g, b, env = struct.unpack_from(">5f", buf, off); off += 20
            kps.append((t, (r, g, b), env))
        out.append(kps)
    return out, off


def decode_numberrange_array(buf, n):
    vals = struct.unpack_from(f">{2 * n}f", buf, 0)
    return [(vals[2 * i], vals[2 * i + 1]) for i in range(n)], 8 * n


def parse_prop_extended(chunks, classes, want):
    """want: {(class_name, prop_name): 'cframe'|'numseq'|'colorseq'|'numrange'}
    -> {(class_name,prop_name): {referent: valeur_decodee}}"""
    results = {}
    for tag, payload in chunks:
        if tag != "PROP":
            continue
        off = 0
        (class_id,) = struct.unpack_from("<I", payload, off); off += 4
        prop_bytes, off = read_string(payload, off)
        dtype = payload[off]; off += 1
        cls = classes.get(class_id)
        if cls is None:
            continue
        key = (cls["name"], prop_bytes.decode("utf-8", "replace"))
        if key not in want:
            continue
        refs = cls["referents"]
        n = len(refs)
        body = payload[off:]
        kind = want[key]
        decoders = {"cframe": decode_cframe_array, "numseq": decode_numbersequence_array,
                    "colorseq": decode_colorsequence_array, "numrange": decode_numberrange_array}
        try:
            entries, _ = decoders[kind](body, n)
            results[key] = dict(zip(refs, entries))
        except Exception as e:
            results[key] = {"_error": f"{type(e).__name__}: {e}"}
    return results


# ---------------------------------------------------------------------

def inventory(path):
    print(f"\n{'=' * 70}\n{path}\n{'=' * 70}")
    version, num_types, num_instances, chunks = read_chunks(path)
    print(f"version={version} num_types={num_types} num_instances={num_instances}")
    classes = parse_inst_chunks(chunks)
    print(f"\n-- classes ({len(classes)}) --")
    for cid, c in sorted(classes.items(), key=lambda kv: -len(kv[1]["referents"])):
        print(f"  {c['name']:<24} x{len(c['referents'])}")
    return classes, chunks


if __name__ == "__main__":
    for p in sys.argv[1:]:
        inventory(p)
