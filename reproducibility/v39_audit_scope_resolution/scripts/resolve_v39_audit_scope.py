import csv
import hashlib
import json
import re
import subprocess
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT_ROOT = ROOT / "reproducibility" / "v39_audit_scope_resolution"
AUDIT_A_DIR = OUT_ROOT / "original_candidate_rule"
AUDIT_B_DIR = OUT_ROOT / "filename_proximity_diagnostic"

TRAIN_MANIFEST = ROOT / "runs" / "component_disjoint_candidates" / "candidate_component_disjoint_v1_train.txt"
VAL_MANIFEST = ROOT / "runs" / "component_disjoint_candidates" / "candidate_component_disjoint_v1_val.txt"
GUARD_MANIFEST = ROOT / "runs" / "component_disjoint_candidates" / "candidate_component_disjoint_v1_guard_unchanged.txt"

CDC_ROOT = ROOT / "reproducibility" / "component_disjoint_split_v1"
INPUT_LOCK = CDC_ROOT / "protocol" / "input_lock.md"
INPUT_LOCK_MANIFEST = CDC_ROOT / "input_snapshot" / "input_lock_manifest.csv"
RGB_HASHES = CDC_ROOT / "input_snapshot" / "rgb_hashes__rgb_hashes.csv"
COMPONENT_NODES = CDC_ROOT / "component_graph" / "component_nodes.csv"
COMPONENT_EDGES = CDC_ROOT / "component_graph" / "component_edges.csv"
COMPONENTS = CDC_ROOT / "component_graph" / "components.csv"
COMPONENT_BUILD_SCRIPT = CDC_ROOT / "scripts" / "build_component_disjoint_split.py"
ASSIGNMENT_PROTOCOL = CDC_ROOT / "assignments" / "assignment_protocol.md"
LOCKED_AUDIT_SUMMARY = CDC_ROOT / "reports" / "candidate_component_disjoint_v1_audit_summary.json"
TVCC_SUMMARY = CDC_ROOT / "input_snapshot" / "train_validation_component_summary__train_val_component_summary.csv"

LEAK_ROOT = ROOT / "reproducibility" / "leakage_audit_v2"
LEAKAGE_SCRIPT = LEAK_ROOT / "scripts" / "run_leakage_audit_v2.py"
ADJUDICATION_SCRIPT = LEAK_ROOT / "scripts" / "run_train_val_adjudication.py"
CODEX_PRELIM_SUMMARY = (
    LEAK_ROOT
    / "review_packet_v1"
    / "codex_preliminary_review"
    / "codex_preliminary_review_summary.json"
)
HUMAN_REVIEW_SHORTLIST = (
    LEAK_ROOT
    / "review_packet_v1"
    / "codex_preliminary_review"
    / "human_review_shortlist.csv"
)

PHASH_THRESHOLD = 4
DHASH_THRESHOLD = 4
FILENAME_GUARD_BAND = 16
STATUS_PASS_PENDING = "V39_ORIGINAL_COMPONENT_RULE_PASS_FILENAME_DIAGNOSTIC_PENDING"
STATUS_FAIL = "V39_ORIGINAL_COMPONENT_RULE_FAIL"
STATUS_BLOCKED = "V39_ORIGINAL_COMPONENT_AUDIT_BLOCKED"


def now_iso():
    return datetime.now().isoformat(timespec="seconds")


def rel(path):
    try:
        return str(path.relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def sha256_file(path):
    if not path.exists():
        return "NA"
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git_commit():
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        return "NA"


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path, rows, fieldnames):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def read_manifest(path):
    return [
        line.strip().strip('"').replace("\\", "/")
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def sample_id_from_rel(row):
    return Path(row).stem


FAMILY_RE = re.compile(r"^(?P<family>.+?)_(?P<num>\d+)$")


def parse_family_id(sample_id):
    m = FAMILY_RE.match(sample_id)
    if not m:
        return "other", None
    family = m.group("family")
    if family not in {"frame", "nframe"}:
        family = "other"
    return family, int(m.group("num"))


def family_rank(family):
    return {"frame": 0, "nframe": 1}.get(family, 2)


class DSU:
    def __init__(self):
        self.parent = {}

    def find(self, item):
        self.parent.setdefault(item, item)
        if self.parent[item] != item:
            self.parent[item] = self.find(self.parent[item])
        return self.parent[item]

    def union(self, a, b):
        ra = self.find(a)
        rb = self.find(b)
        if ra == rb:
            return
        if rb < ra:
            ra, rb = rb, ra
        self.parent[rb] = ra


def load_required_inputs():
    required = [
        TRAIN_MANIFEST,
        VAL_MANIFEST,
        GUARD_MANIFEST,
        INPUT_LOCK,
        INPUT_LOCK_MANIFEST,
        RGB_HASHES,
        COMPONENT_NODES,
        COMPONENT_EDGES,
        COMPONENTS,
        COMPONENT_BUILD_SCRIPT,
        ASSIGNMENT_PROTOCOL,
        LOCKED_AUDIT_SUMMARY,
        TVCC_SUMMARY,
        LEAKAGE_SCRIPT,
        ADJUDICATION_SCRIPT,
        CODEX_PRELIM_SUMMARY,
        HUMAN_REVIEW_SHORTLIST,
    ]
    rows = []
    missing = []
    for path in required:
        exists = path.exists()
        if not exists:
            missing.append(rel(path))
        rows.append(
            {
                "input_path": rel(path),
                "exists": "yes" if exists else "no",
                "size_bytes": path.stat().st_size if exists else "NA",
                "sha256": sha256_file(path),
                "role": input_role(path),
            }
        )
    return rows, missing


def input_role(path):
    if path == TRAIN_MANIFEST:
        return "current V39 train manifest"
    if path == VAL_MANIFEST:
        return "current V39 validation manifest"
    if path == GUARD_MANIFEST:
        return "current V39 guard manifest"
    if path == RGB_HASHES:
        return "locked decoded RGB SHA-256, pHash, dHash table"
    if path == COMPONENT_EDGES:
        return "locked original exact/pHash/dHash candidate graph edges"
    if path == COMPONENT_NODES:
        return "locked original candidate graph component membership"
    if path == COMPONENTS:
        return "locked original component summary and reviewed component mapping"
    if path == COMPONENT_BUILD_SCRIPT:
        return "component graph and split build script"
    if path == LEAKAGE_SCRIPT:
        return "decoded RGB and perceptual hash preprocessing script"
    if path == ADJUDICATION_SCRIPT:
        return "prior train/validation component review script"
    if path == TVCC_SUMMARY:
        return "locked 41 reviewed train/validation components"
    return "supporting locked audit evidence"


def partition_maps(train_rels, val_rels, guard_rels):
    sample_to_rel = {}
    sample_to_partition = {}
    for partition, rows in [
        ("train", train_rels),
        ("validation", val_rels),
        ("guard", guard_rels),
    ]:
        for path in rows:
            sid = sample_id_from_rel(path)
            sample_to_rel[sid] = path
            sample_to_partition[sid] = partition
    return sample_to_rel, sample_to_partition


def load_cdc_components():
    component_nodes = defaultdict(list)
    sid_to_component = {}
    for row in read_csv(COMPONENT_NODES):
        cid = row["component_id"]
        sid = row["sample_id"]
        component_nodes[cid].append(sid)
        sid_to_component[sid] = cid
    component_meta = {row["component_id"]: row for row in read_csv(COMPONENTS)}
    return component_nodes, sid_to_component, component_meta


def high_risk_edge(row):
    return (
        str(row.get("exact_pixel_match", "")).lower() == "true"
        or int(row.get("phash_distance", 9999)) <= PHASH_THRESHOLD
        or int(row.get("dhash_distance", 9999)) <= DHASH_THRESHOLD
    )


def edge_output_row(row, sample_to_rel, sample_to_partition):
    a = row["sample_id_a"]
    b = row["sample_id_b"]
    return {
        "component_id": row["component_id"],
        "sample_id_a": a,
        "sample_id_b": b,
        "v39_partition_a": sample_to_partition.get(a, "NA"),
        "v39_partition_b": sample_to_partition.get(b, "NA"),
        "relative_path_a": sample_to_rel.get(a, "NA"),
        "relative_path_b": sample_to_rel.get(b, "NA"),
        "exact_decoded_rgb_match": row.get("exact_pixel_match", "false"),
        "phash_distance": row.get("phash_distance", "NA"),
        "dhash_distance": row.get("dhash_distance", "NA"),
        "candidate_reason": row.get("candidate_reason", ""),
        "high_risk_edge": "yes" if high_risk_edge(row) else row.get("high_risk_edge", "no"),
        "edge_source": row.get("edge_source", ""),
    }


EDGE_FIELDS = [
    "component_id",
    "sample_id_a",
    "sample_id_b",
    "v39_partition_a",
    "v39_partition_b",
    "relative_path_a",
    "relative_path_b",
    "exact_decoded_rgb_match",
    "phash_distance",
    "dhash_distance",
    "candidate_reason",
    "high_risk_edge",
    "edge_source",
]


def audit_original_rule(sample_to_rel, sample_to_partition, component_nodes, component_meta):
    exact_rows = []
    phash_rows = []
    dhash_rows = []
    cross_edges = []
    secondary_cross_edges = []
    for edge in read_csv(COMPONENT_EDGES):
        a = edge["sample_id_a"]
        b = edge["sample_id_b"]
        pa = sample_to_partition.get(a)
        pb = sample_to_partition.get(b)
        if {pa, pb} != {"train", "validation"}:
            continue
        out = edge_output_row(edge, sample_to_rel, sample_to_partition)
        if high_risk_edge(edge):
            cross_edges.append(out)
            if str(edge.get("exact_pixel_match", "")).lower() == "true":
                exact_rows.append(out)
            if int(edge.get("phash_distance", 9999)) <= PHASH_THRESHOLD:
                phash_rows.append(out)
            if int(edge.get("dhash_distance", 9999)) <= DHASH_THRESHOLD:
                dhash_rows.append(out)
        else:
            secondary_cross_edges.append(out)

    cross_components = []
    component_partition_rows = []
    for cid, nodes in sorted(component_nodes.items()):
        partitions = Counter(sample_to_partition.get(sid, "outside_v39") for sid in nodes)
        partition_set = sorted(p for p in partitions if p in {"train", "validation"})
        meta = component_meta.get(cid, {})
        row = {
            "component_id": cid,
            "node_count": str(len(nodes)),
            "v39_train_count": str(partitions.get("train", 0)),
            "v39_validation_count": str(partitions.get("validation", 0)),
            "v39_guard_count": str(partitions.get("guard", 0)),
            "v39_outside_count": str(partitions.get("outside_v39", 0)),
            "represented_in_both_train_validation": "yes"
            if {"train", "validation"}.issubset(partitions)
            else "no",
            "source_tvcc_components": meta.get("source_tvcc_components", ""),
        }
        component_partition_rows.append(row)
        if row["represented_in_both_train_validation"] == "yes":
            cross_components.append(row)

    write_csv(AUDIT_A_DIR / "exact_decoded_rgb_train_validation_pairs.csv", exact_rows, EDGE_FIELDS)
    write_csv(AUDIT_A_DIR / "phash_le4_train_validation_pairs.csv", phash_rows, EDGE_FIELDS)
    write_csv(AUDIT_A_DIR / "dhash_le4_train_validation_pairs.csv", dhash_rows, EDGE_FIELDS)
    write_csv(AUDIT_A_DIR / "candidate_graph_cross_split_edges.csv", cross_edges, EDGE_FIELDS)
    write_csv(
        AUDIT_A_DIR / "secondary_review_component_cross_split_edges.csv",
        secondary_cross_edges,
        EDGE_FIELDS,
    )
    write_csv(
        AUDIT_A_DIR / "candidate_component_partition_audit.csv",
        component_partition_rows,
        [
            "component_id",
            "node_count",
            "v39_train_count",
            "v39_validation_count",
            "v39_guard_count",
            "v39_outside_count",
            "represented_in_both_train_validation",
            "source_tvcc_components",
        ],
    )
    write_csv(
        AUDIT_A_DIR / "candidate_components_represented_in_both_train_validation.csv",
        cross_components,
        [
            "component_id",
            "node_count",
            "v39_train_count",
            "v39_validation_count",
            "v39_guard_count",
            "v39_outside_count",
            "represented_in_both_train_validation",
            "source_tvcc_components",
        ],
    )
    return {
        "exact_decoded_rgb_train_validation_pairs": len(exact_rows),
        "phash_le4_train_validation_pairs": len(phash_rows),
        "dhash_le4_train_validation_pairs": len(dhash_rows),
        "candidate_graph_cross_split_edges": len(cross_edges),
        "secondary_review_component_cross_split_edges": len(secondary_cross_edges),
        "candidate_components_represented_in_both_train_validation": len(cross_components),
    }


def audit_reviewed_components(sample_to_rel, sample_to_partition, sid_to_component):
    rows = []
    for row in read_csv(TVCC_SUMMARY):
        component_id = row["component_id"]
        samples = []
        for col in ["train_samples", "validation_samples"]:
            if row.get(col):
                samples.extend([s for s in row[col].split("|") if s])
        partitions = Counter(sample_to_partition.get(sid, "outside_v39") for sid in samples)
        cdc_components = sorted({sid_to_component.get(sid, "NA") for sid in samples})
        active_partitions = sorted(p for p in partitions if p in {"train", "validation"})
        rows.append(
            {
                "reviewed_component_id": component_id,
                "sample_count": str(len(samples)),
                "v39_train_count": str(partitions.get("train", 0)),
                "v39_validation_count": str(partitions.get("validation", 0)),
                "v39_guard_count": str(partitions.get("guard", 0)),
                "v39_outside_count": str(partitions.get("outside_v39", 0)),
                "v39_partition_set": "|".join(active_partitions) if active_partitions else "NA",
                "wholly_assigned_to_one_side": "yes" if len(active_partitions) <= 1 else "no",
                "cdc_component_ids": "|".join(cdc_components),
                "codex_reviewer_label": row.get("reviewer_label", ""),
            }
        )
    rows.sort(key=lambda r: r["reviewed_component_id"])
    write_csv(
        AUDIT_A_DIR / "reviewed_41_component_assignment.csv",
        rows,
        [
            "reviewed_component_id",
            "sample_count",
            "v39_train_count",
            "v39_validation_count",
            "v39_guard_count",
            "v39_outside_count",
            "v39_partition_set",
            "wholly_assigned_to_one_side",
            "cdc_component_ids",
            "codex_reviewer_label",
        ],
    )
    total = len(rows)
    wholly = sum(1 for r in rows if r["wholly_assigned_to_one_side"] == "yes")
    return {
        "reviewed_components_total": total,
        "reviewed_components_wholly_assigned_to_one_side": wholly,
        "reviewed_components_split_across_train_validation": total - wholly,
    }


def rgb_guard_overlap_summary(train_ids, val_ids, guard_ids):
    hash_to_parts = defaultdict(lambda: defaultdict(set))
    for row in read_csv(RGB_HASHES):
        sid = row["sample_id"]
        if sid in train_ids:
            hash_to_parts[row["rgb_pixel_sha256"]]["train"].add(sid)
        if sid in val_ids:
            hash_to_parts[row["rgb_pixel_sha256"]]["validation"].add(sid)
        if sid in guard_ids:
            hash_to_parts[row["rgb_pixel_sha256"]]["guard"].add(sid)
    rows = []
    pairs = [
        ("train", "validation"),
        ("train", "guard"),
        ("validation", "guard"),
    ]
    for a, b in pairs:
        groups = 0
        pair_count = 0
        for h, parts in hash_to_parts.items():
            if parts.get(a) and parts.get(b):
                groups += 1
                pair_count += len(parts[a]) * len(parts[b])
        rows.append(
            {
                "partition_pair": f"{a}-{b}",
                "exact_rgb_group_count": str(groups),
                "exact_rgb_pair_count": str(pair_count),
            }
        )
    write_csv(
        AUDIT_A_DIR / "guard_exact_rgb_overlap_diagnostic.csv",
        rows,
        ["partition_pair", "exact_rgb_group_count", "exact_rgb_pair_count"],
    )
    return {r["partition_pair"]: int(r["exact_rgb_group_count"]) for r in rows}


def load_tvcc_membership():
    sid_to_tvcc = defaultdict(set)
    for row in read_csv(TVCC_SUMMARY):
        cid = row["component_id"]
        for col in ["train_samples", "validation_samples"]:
            for sid in row.get(col, "").split("|"):
                if sid:
                    sid_to_tvcc[sid].add(cid)
    return sid_to_tvcc


def filename_proximity_pairs(train_rels, val_rels, sid_to_component, sid_to_tvcc):
    train_by_family = defaultdict(list)
    train_rel_by_sid = {}
    for path in train_rels:
        sid = sample_id_from_rel(path)
        family, number = parse_family_id(sid)
        if number is None:
            continue
        train_by_family[family].append((number, path, sid))
        train_rel_by_sid[sid] = path
    for family in train_by_family:
        train_by_family[family].sort(key=lambda item: (item[0], item[1], item[2]))

    rows = []
    for path in sorted(val_rels):
        vsid = sample_id_from_rel(path)
        family, number = parse_family_id(vsid)
        if number is None:
            continue
        best = None
        for tnum, tpath, tsid in train_by_family.get(family, []):
            distance = abs(number - tnum)
            if distance <= FILENAME_GUARD_BAND:
                candidate = (distance, tnum, tpath, tsid)
                if best is None or candidate < best:
                    best = candidate
            elif tnum > number + FILENAME_GUARD_BAND:
                break
        if best is None:
            continue
        distance, tnum, tpath, tsid = best
        v_cdc = sid_to_component.get(vsid, "NA")
        t_cdc = sid_to_component.get(tsid, "NA")
        same_cdc = v_cdc != "NA" and v_cdc == t_cdc
        v_tvcc = sorted(sid_to_tvcc.get(vsid, set()))
        t_tvcc = sorted(sid_to_tvcc.get(tsid, set()))
        common_tvcc = sorted(set(v_tvcc) & set(t_tvcc))
        if common_tvcc:
            bucket = "covered_by_reviewed_41_component"
        elif same_cdc:
            bucket = "covered_by_original_candidate_graph"
        elif v_tvcc or t_tvcc:
            bucket = "endpoint_in_reviewed_41_only"
        else:
            bucket = "not_covered_by_original_graph"
        rows.append(
            {
                "pair_id": "",
                "family": family,
                "validation_sample_id": vsid,
                "validation_relative_path": path,
                "validation_numeric_id": str(number),
                "nearest_train_sample_id": tsid,
                "nearest_train_relative_path": tpath,
                "train_numeric_id": str(tnum),
                "id_distance": str(distance),
                "same_original_candidate_component": "yes" if same_cdc else "no",
                "validation_cdc_component_id": v_cdc,
                "train_cdc_component_id": t_cdc,
                "same_reviewed_41_component": "yes" if common_tvcc else "no",
                "reviewed_41_component_ids": "|".join(common_tvcc) if common_tvcc else "NA",
                "validation_reviewed_41_component_ids": "|".join(v_tvcc) if v_tvcc else "NA",
                "train_reviewed_41_component_ids": "|".join(t_tvcc) if t_tvcc else "NA",
                "relation_bucket": bucket,
                "diagnostic_rule": f"same-family nearest train ID distance <= {FILENAME_GUARD_BAND}",
                "capture_order_claim": "not_claimed",
                "selection_basis": "family numeric ID distance only",
            }
        )
    rows.sort(
        key=lambda r: (
            family_rank(r["family"]),
            int(r["id_distance"]),
            r["validation_sample_id"],
            r["nearest_train_sample_id"],
        )
    )
    for idx, row in enumerate(rows, 1):
        row["pair_id"] = f"fp_{idx:04d}"
    return rows


PAIR_FIELDS = [
    "pair_id",
    "family",
    "validation_sample_id",
    "validation_relative_path",
    "validation_numeric_id",
    "nearest_train_sample_id",
    "nearest_train_relative_path",
    "train_numeric_id",
    "id_distance",
    "same_original_candidate_component",
    "validation_cdc_component_id",
    "train_cdc_component_id",
    "same_reviewed_41_component",
    "reviewed_41_component_ids",
    "validation_reviewed_41_component_ids",
    "train_reviewed_41_component_ids",
    "relation_bucket",
    "diagnostic_rule",
    "capture_order_claim",
    "selection_basis",
]


def build_filename_clusters(pairs):
    uncovered = [r for r in pairs if r["same_original_candidate_component"] == "no"]
    dsu = DSU()
    for row in uncovered:
        dsu.union(row["validation_sample_id"], row["nearest_train_sample_id"])
    cluster_nodes = defaultdict(set)
    for item in list(dsu.parent):
        cluster_nodes[dsu.find(item)].add(item)

    temp_clusters = []
    for root, nodes in cluster_nodes.items():
        cluster_pairs = [
            r
            for r in uncovered
            if r["validation_sample_id"] in nodes or r["nearest_train_sample_id"] in nodes
        ]
        families = sorted({r["family"] for r in cluster_pairs})
        min_distance = min(int(r["id_distance"]) for r in cluster_pairs)
        lexical_min = min(
            min(r["validation_sample_id"], r["nearest_train_sample_id"]) for r in cluster_pairs
        )
        cluster_family = families[0] if len(families) == 1 else "mixed"
        temp_clusters.append(
            {
                "cluster_family": cluster_family,
                "sort_key": (family_rank(cluster_family), min_distance, lexical_min),
                "min_id_distance": min_distance,
                "lexical_min_sample_id": lexical_min,
                "nodes": sorted(nodes),
                "pairs": sorted(
                    cluster_pairs,
                    key=lambda r: (
                        family_rank(r["family"]),
                        int(r["id_distance"]),
                        r["validation_sample_id"],
                        r["nearest_train_sample_id"],
                    ),
                ),
            }
        )
    temp_clusters.sort(key=lambda c: c["sort_key"])

    cluster_rows = []
    review_pairs = []
    shortlist = []
    for idx, cluster in enumerate(temp_clusters, 1):
        cluster_id = f"fpc_{idx:04d}"
        pair_ids = [r["pair_id"] for r in cluster["pairs"]]
        val_nodes = sorted({r["validation_sample_id"] for r in cluster["pairs"]})
        train_nodes = sorted({r["nearest_train_sample_id"] for r in cluster["pairs"]})
        cluster_rows.append(
            {
                "cluster_id": cluster_id,
                "family": cluster["cluster_family"],
                "pair_count": str(len(cluster["pairs"])),
                "node_count": str(len(cluster["nodes"])),
                "validation_node_count": str(len(val_nodes)),
                "train_node_count": str(len(train_nodes)),
                "min_id_distance": str(cluster["min_id_distance"]),
                "lexical_min_sample_id": cluster["lexical_min_sample_id"],
                "pair_ids": "|".join(pair_ids),
                "sample_ids": "|".join(cluster["nodes"]),
            }
        )
        for order, row in enumerate(cluster["pairs"], 1):
            out = dict(row)
            out["cluster_id"] = cluster_id
            out["cluster_pair_order"] = str(order)
            review_pairs.append(out)
        rep = dict(cluster["pairs"][0])
        rep["shortlist_rank"] = str(idx)
        rep["cluster_id"] = cluster_id
        rep["cluster_pair_count"] = str(len(cluster["pairs"]))
        rep["cluster_node_count"] = str(len(cluster["nodes"]))
        rep["review_selection_rule"] = (
            "first pair after cluster sort by family, minimum ID distance, lexical sample ID"
        )
        shortlist.append(rep)
    return cluster_rows, review_pairs, shortlist


def summarize_filename_diagnostic(pairs, clusters, review_pairs, shortlist):
    family_rows = []
    family_counter = Counter(r["family"] for r in pairs)
    for family in sorted(family_counter, key=family_rank):
        subset = [r for r in pairs if r["family"] == family]
        family_rows.append(
            {
                "family": family,
                "pair_count": str(len(subset)),
                "covered_by_original_candidate_graph": str(
                    sum(1 for r in subset if r["same_original_candidate_component"] == "yes")
                ),
                "covered_by_reviewed_41_component": str(
                    sum(1 for r in subset if r["same_reviewed_41_component"] == "yes")
                ),
                "not_covered_by_original_graph": str(
                    sum(1 for r in subset if r["same_original_candidate_component"] == "no")
                ),
            }
        )
    distance_rows = [
        {"id_distance": str(distance), "pair_count": str(count)}
        for distance, count in sorted(Counter(int(r["id_distance"]) for r in pairs).items())
    ]
    relation_rows = [
        {"relation_bucket": bucket, "pair_count": str(count)}
        for bucket, count in sorted(Counter(r["relation_bucket"] for r in pairs).items())
    ]
    write_csv(AUDIT_B_DIR / "filename_proximity_pairs.csv", pairs, PAIR_FIELDS)
    write_csv(
        AUDIT_B_DIR / "family_summary.csv",
        family_rows,
        [
            "family",
            "pair_count",
            "covered_by_original_candidate_graph",
            "covered_by_reviewed_41_component",
            "not_covered_by_original_graph",
        ],
    )
    write_csv(AUDIT_B_DIR / "id_distance_distribution.csv", distance_rows, ["id_distance", "pair_count"])
    write_csv(AUDIT_B_DIR / "component_relation_summary.csv", relation_rows, ["relation_bucket", "pair_count"])
    write_csv(
        AUDIT_B_DIR / "uncovered_filename_proximity_clusters.csv",
        clusters,
        [
            "cluster_id",
            "family",
            "pair_count",
            "node_count",
            "validation_node_count",
            "train_node_count",
            "min_id_distance",
            "lexical_min_sample_id",
            "pair_ids",
            "sample_ids",
        ],
    )
    write_csv(AUDIT_B_DIR / "uncovered_filename_proximity_pairs.csv", review_pairs, ["cluster_id", "cluster_pair_order"] + PAIR_FIELDS)
    write_csv(
        AUDIT_B_DIR / "human_review_shortlist.csv",
        shortlist,
        [
            "shortlist_rank",
            "cluster_id",
            "cluster_pair_count",
            "cluster_node_count",
            "review_selection_rule",
        ]
        + PAIR_FIELDS,
    )
    return {
        "filename_proximity_pair_count": len(pairs),
        "family_counts": dict(family_counter),
        "id_distance_distribution": {str(k): v for k, v in Counter(int(r["id_distance"]) for r in pairs).items()},
        "covered_by_original_candidate_graph": sum(
            1 for r in pairs if r["same_original_candidate_component"] == "yes"
        ),
        "covered_by_reviewed_41_component": sum(
            1 for r in pairs if r["same_reviewed_41_component"] == "yes"
        ),
        "not_covered_by_original_graph": sum(
            1 for r in pairs if r["same_original_candidate_component"] == "no"
        ),
        "uncovered_cluster_count": len(clusters),
        "human_review_shortlist_count": len(shortlist),
    }


def write_audit_a_report(summary, reviewed_summary, guard_overlap, missing_inputs, input_manifest):
    rows = [
        {
            "metric": key,
            "value": str(value),
            "notes": audit_a_note(key),
        }
        for key, value in {**summary, **reviewed_summary}.items()
    ]
    rows.extend(
        [
            {
                "metric": "train_guard_exact_rgb_groups",
                "value": str(guard_overlap.get("train-guard", 0)),
                "notes": "guard diagnostic only; guard is not an independent test partition",
            },
            {
                "metric": "validation_guard_exact_rgb_groups",
                "value": str(guard_overlap.get("validation-guard", 0)),
                "notes": "guard diagnostic only; guard is not an independent test partition",
            },
            {
                "metric": "missing_required_original_inputs",
                "value": str(len(missing_inputs)),
                "notes": "|".join(missing_inputs) if missing_inputs else "none",
            },
        ]
    )
    write_csv(AUDIT_A_DIR / "original_candidate_rule_summary.csv", rows, ["metric", "value", "notes"])
    write_csv(AUDIT_A_DIR / "input_evidence_manifest.csv", input_manifest, ["input_path", "exists", "size_bytes", "sha256", "role"])
    lines = [
        "# V39 Audit A: Original Candidate-Component Rule",
        "",
        f"- Generated: {now_iso()}",
        f"- Git commit: `{git_commit()}`",
        "- Rule: decoded RGB exact match, pHash Hamming <= 4, dHash Hamming <= 4, connected components over the locked candidate graph.",
        "- Preprocessing source: channels 0:3 from TriAir `.npy`; decoded RGB array SHA-256; 64-bit pHash and dHash from the locked leakage-audit script.",
        "- The filename-ID rule is not used in Audit A.",
        "",
        "## Metrics",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
    ]
    for row in rows:
        lines.append(f"| {row['metric']} | {row['value']} |")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- Audit A passes the original exact/pHash/dHash component rule for train/validation if all cross-split pair, edge, and component counts are zero and all 41 reviewed components are wholly assigned to one side.",
            "- Guard overlap disqualifies the guard partition from independent-test use, but does not by itself determine train/validation component integrity.",
        ]
    )
    (AUDIT_A_DIR / "original_candidate_rule_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def audit_a_note(key):
    notes = {
        "exact_decoded_rgb_train_validation_pairs": "decoded RGB SHA-256 exact train/validation pairs",
        "phash_le4_train_validation_pairs": "locked pHash Hamming <= 4 train/validation pairs",
        "dhash_le4_train_validation_pairs": "locked dHash Hamming <= 4 train/validation pairs",
        "candidate_graph_cross_split_edges": "direct high-risk candidate edges crossing current V39 train/validation",
        "secondary_review_component_cross_split_edges": "retained reviewed-component secondary edges crossing current V39 train/validation",
        "candidate_components_represented_in_both_train_validation": "locked components containing both current train and validation samples",
        "reviewed_components_total": "previously reviewed train/validation perceptual components",
        "reviewed_components_wholly_assigned_to_one_side": "reviewed components wholly in current train or current validation",
        "reviewed_components_split_across_train_validation": "reviewed components split across current train and validation",
    }
    return notes.get(key, "")


def write_filename_report(summary):
    lines = [
        "# V39 Audit B: Filename-Proximity Diagnostic",
        "",
        f"- Generated: {now_iso()}",
        f"- Rule: same-family nearest train numeric ID within <= {FILENAME_GUARD_BAND} for each validation sample.",
        "- This is a diagnostic proxy only; it is not treated as proof of capture order.",
        "- Selection uses filename family and numeric ID distance only, not model output, labels, or visual appearance.",
        "",
        "## Metrics",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| filename_proximity_pair_count | {summary['filename_proximity_pair_count']} |",
        f"| covered_by_original_candidate_graph | {summary['covered_by_original_candidate_graph']} |",
        f"| covered_by_reviewed_41_component | {summary['covered_by_reviewed_41_component']} |",
        f"| not_covered_by_original_graph | {summary['not_covered_by_original_graph']} |",
        f"| uncovered_cluster_count | {summary['uncovered_cluster_count']} |",
        f"| human_review_shortlist_count | {summary['human_review_shortlist_count']} |",
        "",
        "## Review Package",
        "",
        "- Full pair table: `filename_proximity_pairs.csv`.",
        "- Uncovered full review package: `uncovered_filename_proximity_pairs.csv`.",
        "- Cluster table: `uncovered_filename_proximity_clusters.csv`.",
        "- Deterministic representative shortlist: `human_review_shortlist.csv`.",
    ]
    (AUDIT_B_DIR / "filename_proximity_diagnostic_report.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )


def write_decision_report(status, audit_a, audit_b, reviewed, guard_overlap, missing_inputs):
    decision = {
        "generated_at": now_iso(),
        "git_commit": git_commit(),
        "status": status,
        "audit_a": audit_a,
        "reviewed_41_components": reviewed,
        "audit_b": audit_b,
        "guard_overlap": guard_overlap,
        "guard_overlap_statement": (
            "Guard overlap disqualifies the guard partition from independent-test use, "
            "but does not by itself determine train/validation component integrity."
        ),
        "missing_original_inputs": missing_inputs,
        "training_started": False,
        "split_changed": False,
        "manuscript_changed": False,
        "next_gate": (
            "No new V39 training until filename-proximity review is completed, or until future claims "
            "are explicitly narrowed to the fixed perceptual candidate rule."
            if status == STATUS_PASS_PENDING
            else "Resolve Audit A failure or blocked evidence before any V39 continuation."
        ),
    }
    write_json(OUT_ROOT / "V39_AUDIT_SCOPE_RESOLUTION.json", decision)

    lines = [
        "# V39 Audit-Scope Resolution",
        "",
        f"- Generated: {decision['generated_at']}",
        f"- Git commit: `{decision['git_commit']}`",
        f"- Status: `{status}`",
        "",
        "## Decision",
        "",
    ]
    if status == STATUS_PASS_PENDING:
        lines.extend(
            [
                "Audit A passes under the original exact/pHash/dHash candidate-component rule for the current V39 train/validation manifests.",
                "",
                "Filename proximity remains an unresolved diagnostic risk: the 353 same-family nearest-ID candidates are not covered by the original perceptual candidate graph and require human review, or future claims must be narrowed to the fixed perceptual candidate rule.",
            ]
        )
    elif status == STATUS_FAIL:
        lines.append(
            "Audit A fails under the original exact/pHash/dHash candidate-component rule; V39 must remain exploratory until a new split-design task resolves the failure."
        )
    else:
        lines.append(
            "Audit A is blocked because the original graph inputs or preprocessing evidence could not be recovered."
        )
    lines.extend(
        [
            "",
            "Guard overlap disqualifies the guard partition from independent-test use, but does not by itself determine train/validation component integrity.",
            "",
            "## Audit A: Original Candidate Rule",
            "",
            "| Metric | Value |",
            "| --- | ---: |",
            f"| exact decoded-RGB train/validation pairs | {audit_a['exact_decoded_rgb_train_validation_pairs']} |",
            f"| pHash <= 4 train/validation pairs | {audit_a['phash_le4_train_validation_pairs']} |",
            f"| dHash <= 4 train/validation pairs | {audit_a['dhash_le4_train_validation_pairs']} |",
            f"| candidate-graph cross-split edges | {audit_a['candidate_graph_cross_split_edges']} |",
            f"| candidate components in both train and validation | {audit_a['candidate_components_represented_in_both_train_validation']} |",
            f"| reviewed 41 components wholly assigned | {reviewed['reviewed_components_wholly_assigned_to_one_side']} / {reviewed['reviewed_components_total']} |",
            "",
            "## Audit B: Filename-Proximity Diagnostic",
            "",
            "| Metric | Value |",
            "| --- | ---: |",
            f"| same-family nearest-ID candidates | {audit_b['filename_proximity_pair_count']} |",
            f"| covered by original perceptual graph | {audit_b['covered_by_original_candidate_graph']} |",
            f"| covered by reviewed 41 component | {audit_b['covered_by_reviewed_41_component']} |",
            f"| not covered by original graph | {audit_b['not_covered_by_original_graph']} |",
            f"| uncovered clusters | {audit_b['uncovered_cluster_count']} |",
            f"| deterministic shortlist rows | {audit_b['human_review_shortlist_count']} |",
            "",
            "## Outputs",
            "",
            "- Audit A outputs: `original_candidate_rule/`.",
            "- Audit B outputs: `filename_proximity_diagnostic/`.",
            "- No training, split change, manuscript edit, checkpoint change, raw-data change, or label change was performed.",
        ]
    )
    (OUT_ROOT / "V39_AUDIT_SCOPE_RESOLUTION.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    for directory in [AUDIT_A_DIR, AUDIT_B_DIR]:
        directory.mkdir(parents=True, exist_ok=True)

    input_manifest, missing_inputs = load_required_inputs()
    train_rels = read_manifest(TRAIN_MANIFEST)
    val_rels = read_manifest(VAL_MANIFEST)
    guard_rels = read_manifest(GUARD_MANIFEST)
    train_ids = {sample_id_from_rel(p) for p in train_rels}
    val_ids = {sample_id_from_rel(p) for p in val_rels}
    guard_ids = {sample_id_from_rel(p) for p in guard_rels}
    sample_to_rel, sample_to_partition = partition_maps(train_rels, val_rels, guard_rels)
    component_nodes, sid_to_component, component_meta = load_cdc_components()

    if missing_inputs:
        audit_a_summary = {
            "exact_decoded_rgb_train_validation_pairs": "NA",
            "phash_le4_train_validation_pairs": "NA",
            "dhash_le4_train_validation_pairs": "NA",
            "candidate_graph_cross_split_edges": "NA",
            "secondary_review_component_cross_split_edges": "NA",
            "candidate_components_represented_in_both_train_validation": "NA",
        }
        reviewed_summary = {
            "reviewed_components_total": "NA",
            "reviewed_components_wholly_assigned_to_one_side": "NA",
            "reviewed_components_split_across_train_validation": "NA",
        }
        guard_overlap = {}
        audit_b_summary = {}
        status = STATUS_BLOCKED
    else:
        audit_a_summary = audit_original_rule(
            sample_to_rel, sample_to_partition, component_nodes, component_meta
        )
        reviewed_summary = audit_reviewed_components(sample_to_rel, sample_to_partition, sid_to_component)
        guard_overlap = rgb_guard_overlap_summary(train_ids, val_ids, guard_ids)
        write_audit_a_report(audit_a_summary, reviewed_summary, guard_overlap, missing_inputs, input_manifest)

        sid_to_tvcc = load_tvcc_membership()
        proximity_pairs = filename_proximity_pairs(train_rels, val_rels, sid_to_component, sid_to_tvcc)
        clusters, review_pairs, shortlist = build_filename_clusters(proximity_pairs)
        audit_b_summary = summarize_filename_diagnostic(
            proximity_pairs, clusters, review_pairs, shortlist
        )
        write_filename_report(audit_b_summary)

        audit_a_pass = (
            audit_a_summary["exact_decoded_rgb_train_validation_pairs"] == 0
            and audit_a_summary["phash_le4_train_validation_pairs"] == 0
            and audit_a_summary["dhash_le4_train_validation_pairs"] == 0
            and audit_a_summary["candidate_graph_cross_split_edges"] == 0
            and audit_a_summary["candidate_components_represented_in_both_train_validation"] == 0
            and reviewed_summary["reviewed_components_total"] == 41
            and reviewed_summary["reviewed_components_split_across_train_validation"] == 0
        )
        status = STATUS_PASS_PENDING if audit_a_pass else STATUS_FAIL

    write_csv(
        AUDIT_A_DIR / "input_evidence_manifest.csv",
        input_manifest,
        ["input_path", "exists", "size_bytes", "sha256", "role"],
    )
    write_decision_report(status, audit_a_summary, audit_b_summary, reviewed_summary, guard_overlap, missing_inputs)
    print(json.dumps({"status": status, "audit_a": audit_a_summary, "audit_b": audit_b_summary}, indent=2))


if __name__ == "__main__":
    main()
