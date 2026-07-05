import csv
import hashlib
import html
import json
import math
import shutil
import subprocess
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
DATA_ROOT = Path(r"D:\download\triair")
OUT_ROOT = ROOT / "reproducibility" / "v39_filename_proximity_review_packet_v1"
AUDIT_ROOT = ROOT / "reproducibility" / "v39_audit_scope_resolution"

TRAIN_MANIFEST = ROOT / "runs" / "component_disjoint_candidates" / "candidate_component_disjoint_v1_train.txt"
VAL_MANIFEST = ROOT / "runs" / "component_disjoint_candidates" / "candidate_component_disjoint_v1_val.txt"
FILENAME_PAIRS = AUDIT_ROOT / "filename_proximity_diagnostic" / "filename_proximity_pairs.csv"
UNCOVERED_PAIRS = AUDIT_ROOT / "filename_proximity_diagnostic" / "uncovered_filename_proximity_pairs.csv"
UNCOVERED_CLUSTERS = AUDIT_ROOT / "filename_proximity_diagnostic" / "uncovered_filename_proximity_clusters.csv"
AUDIT_SHORTLIST = AUDIT_ROOT / "filename_proximity_diagnostic" / "human_review_shortlist.csv"
AUDIT_DECISION_MD = AUDIT_ROOT / "V39_AUDIT_SCOPE_RESOLUTION.md"
AUDIT_DECISION_JSON = AUDIT_ROOT / "V39_AUDIT_SCOPE_RESOLUTION.json"
REVIEWED_41_ASSIGNMENT = AUDIT_ROOT / "original_candidate_rule" / "reviewed_41_component_assignment.csv"

COMPONENT_GRAPH_ROOT = ROOT / "reproducibility" / "component_disjoint_split_v1" / "component_graph"
COMPONENT_NODES = COMPONENT_GRAPH_ROOT / "component_nodes.csv"
COMPONENT_EDGES = COMPONENT_GRAPH_ROOT / "component_edges.csv"
COMPONENTS = COMPONENT_GRAPH_ROOT / "components.csv"
RGB_HASHES = ROOT / "reproducibility" / "component_disjoint_split_v1" / "input_snapshot" / "rgb_hashes__rgb_hashes.csv"

VALID_FINAL_LABELS = [
    "exact_duplicate",
    "adjacent_or_near_identical",
    "same_scene_distinct_observation",
    "false_candidate",
    "uncertain",
]
LABEL_PRECEDENCE = {
    "exact_duplicate": 0,
    "adjacent_or_near_identical": 1,
    "uncertain": 2,
    "same_scene_distinct_observation": 3,
    "false_candidate": 4,
}

PAIR_SELECT_LIMIT = 10
OVERVIEW_PAIR_LIMIT = 4


def now_iso():
    return datetime.now().isoformat(timespec="seconds")


def repo_rel(path):
    p = Path(path)
    try:
        return str(p.resolve().relative_to(ROOT.resolve())).replace("\\", "/")
    except Exception:
        return str(p).replace("\\", "/")


def safe_name(text):
    return "".join(c if c.isalnum() or c in "._-" else "_" for c in str(text))


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
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def write_csv(path, rows, fieldnames):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def read_manifest(path):
    return [
        line.strip().strip('"').replace("\\", "/")
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def load_rgb(relative_path):
    path = DATA_ROOT / relative_path
    arr = np.load(path, mmap_mode="r")
    if arr.ndim != 3 or arr.shape[2] < 3:
        raise ValueError(f"expected HxWxC with >=3 channels, got {arr.shape}: {path}")
    rgb = np.array(arr[:, :, :3]).astype(np.float32)
    finite = np.isfinite(rgb)
    if not finite.all():
        rgb = np.where(finite, rgb, 0.0)
    if rgb.size:
        min_val = float(rgb.min())
        max_val = float(rgb.max())
        if max_val <= 1.5 and min_val >= -0.1:
            rgb = rgb * 255.0
    return np.clip(rgb, 0, 255).astype(np.uint8)


def resize_rgb(rgb, size=(256, 192)):
    return Image.fromarray(rgb).resize(size, Image.Resampling.BILINEAR)


def image_similarity_stats(train_rel, val_rel, rgb_hash_by_sid):
    train_rgb = load_rgb(train_rel)
    val_rgb = load_rgb(val_rel)
    exact_rgb = "yes" if rgb_hash_by_sid.get(Path(train_rel).stem) == rgb_hash_by_sid.get(Path(val_rel).stem) else "no"
    a = np.asarray(resize_rgb(train_rgb, (160, 120))).astype(np.float32)
    b = np.asarray(resize_rgb(val_rgb, (160, 120))).astype(np.float32)
    diff = np.abs(a - b)
    mae = float(diff.mean())
    p95 = float(np.percentile(diff, 95))
    return {
        "exact_decoded_rgb_match": exact_rgb,
        "resized_rgb_mae": f"{mae:.6f}",
        "resized_rgb_absdiff_p95": f"{p95:.6f}",
    }


def default_font(size=16):
    for candidate in [
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibri.ttf",
    ]:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


FONT = default_font(16)
FONT_SMALL = default_font(13)
FONT_TITLE = default_font(20)


def wrap_text(draw, text, font, max_width):
    words = str(text).split()
    if not words:
        return [""]
    lines = []
    current = words[0]
    for word in words[1:]:
        trial = current + " " + word
        if draw.textbbox((0, 0), trial, font=font)[2] <= max_width:
            current = trial
        else:
            lines.append(current)
            current = word
    lines.append(current)
    wrapped = []
    for line in lines:
        if draw.textbbox((0, 0), line, font=font)[2] <= max_width:
            wrapped.append(line)
            continue
        segment = ""
        for ch in line:
            trial = segment + ch
            if draw.textbbox((0, 0), trial, font=font)[2] <= max_width:
                segment = trial
            else:
                wrapped.append(segment)
                segment = ch
        if segment:
            wrapped.append(segment)
    return wrapped


def draw_lines(draw, x, y, lines, font=FONT_SMALL, fill=(0, 0, 0), line_gap=17):
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        y += line_gap
    return y


def draw_sample_tile(
    draw,
    canvas,
    x,
    y,
    w,
    h,
    image,
    partition,
    sample_id,
    relative_path,
    family,
    numeric_id,
    id_distance,
    cluster_id,
):
    color = (32, 92, 190) if partition == "TRAIN" else (206, 92, 32)
    draw.rectangle((x, y, x + w, y + h), outline=color, width=4)
    label_lines = [
        f"partition: {partition}",
        f"sample ID: {sample_id}",
        f"family: {family}",
        f"numeric ID: {numeric_id}",
        f"ID distance: {id_distance}",
        f"cluster ID: {cluster_id}",
        f"path: {relative_path}",
    ]
    text_y = y + 8
    for idx, line in enumerate(label_lines):
        wrapped = wrap_text(draw, line, FONT_SMALL, w - 20)
        text_y = draw_lines(draw, x + 10, text_y, wrapped, font=FONT_SMALL, fill=color if idx == 0 else (0, 0, 0))
    img_h = max(80, h - (text_y - y) - 18)
    img = image.copy()
    img.thumbnail((w - 18, img_h), Image.Resampling.BILINEAR)
    img_x = x + (w - img.width) // 2
    img_y = y + h - img.height - 8
    canvas.paste(img, (img_x, img_y))


def make_overview(cluster_id, selected_pairs, out_path):
    pair_count = min(len(selected_pairs), OVERVIEW_PAIR_LIMIT)
    pair_rows = selected_pairs[:pair_count]
    tile_w, tile_h = 360, 320
    gap = 22
    header_h = 58
    canvas_w = gap + 2 * tile_w + gap
    canvas_h = header_h + pair_count * (tile_h + gap) + gap
    canvas = Image.new("RGB", (canvas_w, canvas_h), "white")
    draw = ImageDraw.Draw(canvas)
    draw.text((gap, 18), f"cluster ID: {cluster_id}", font=FONT_TITLE, fill=(0, 0, 0))
    for idx, row in enumerate(pair_rows):
        y = header_h + idx * (tile_h + gap)
        train_img = resize_rgb(load_rgb(row["nearest_train_relative_path"]), (330, 210))
        val_img = resize_rgb(load_rgb(row["validation_relative_path"]), (330, 210))
        draw_sample_tile(
            draw,
            canvas,
            gap,
            y,
            tile_w,
            tile_h,
            train_img,
            "TRAIN",
            row["nearest_train_sample_id"],
            row["nearest_train_relative_path"],
            row["family"],
            row["train_numeric_id"],
            row["id_distance"],
            cluster_id,
        )
        draw_sample_tile(
            draw,
            canvas,
            gap + tile_w + gap,
            y,
            tile_w,
            tile_h,
            val_img,
            "VALIDATION",
            row["validation_sample_id"],
            row["validation_relative_path"],
            row["family"],
            row["validation_numeric_id"],
            row["id_distance"],
            cluster_id,
        )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out_path)
    return out_path


def make_pair_review_pdf(cluster_id, selected_pairs, out_path):
    pages = []
    for row in selected_pairs:
        canvas = Image.new("RGB", (900, 660), "white")
        draw = ImageDraw.Draw(canvas)
        draw.text((28, 18), f"cluster ID: {cluster_id}", font=FONT_TITLE, fill=(0, 0, 0))
        train_img = resize_rgb(load_rgb(row["nearest_train_relative_path"]), (390, 260))
        val_img = resize_rgb(load_rgb(row["validation_relative_path"]), (390, 260))
        draw_sample_tile(
            draw,
            canvas,
            28,
            66,
            400,
            560,
            train_img,
            "TRAIN",
            row["nearest_train_sample_id"],
            row["nearest_train_relative_path"],
            row["family"],
            row["train_numeric_id"],
            row["id_distance"],
            cluster_id,
        )
        draw_sample_tile(
            draw,
            canvas,
            472,
            66,
            400,
            560,
            val_img,
            "VALIDATION",
            row["validation_sample_id"],
            row["validation_relative_path"],
            row["family"],
            row["validation_numeric_id"],
            row["id_distance"],
            cluster_id,
        )
        pages.append(canvas.convert("RGB"))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if pages:
        pages[0].save(out_path, "PDF", save_all=True, append_images=pages[1:], resolution=96.0, quality=75)
    return out_path


def make_overview_packet_pdf(overview_paths, out_path):
    pages = [Image.open(path).convert("RGB") for path in overview_paths]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if pages:
        pages[0].save(out_path, "PDF", save_all=True, append_images=pages[1:], resolution=96.0, quality=75)


def pair_relation_fields(row, edge_set):
    key = tuple(sorted([row["validation_sample_id"], row["nearest_train_sample_id"]]))
    pair_is_edge = "yes" if key in edge_set else "no"
    same_reviewed = "yes" if row.get("same_reviewed_41_component") == "yes" else "no"
    val_reviewed = row.get("validation_reviewed_41_component_ids", "NA") not in {"", "NA"}
    train_reviewed = row.get("train_reviewed_41_component_ids", "NA") not in {"", "NA"}
    one_or_more = "yes" if val_reviewed or train_reviewed else "no"
    neither = "yes" if not (val_reviewed or train_reviewed) else "no"
    return {
        "pair_is_original_candidate_graph_edge": pair_is_edge,
        "endpoints_in_same_reviewed_component": same_reviewed,
        "one_or_more_endpoint_in_reviewed_component": one_or_more,
        "neither_endpoint_in_reviewed_component": neither,
    }


def preliminary_label_for_cluster(cluster_pairs):
    selected_stats = cluster_pairs
    exact_count = sum(1 for row in selected_stats if row["exact_decoded_rgb_match"] == "yes")
    min_distance = min(int(row["id_distance"]) for row in selected_stats)
    min_mae = min(float(row["resized_rgb_mae"]) for row in selected_stats)
    pair_count = len(selected_stats)
    if exact_count > 0:
        return "exact_duplicate", "high", "At least one selected pair has exact decoded RGB equality."
    if min_distance <= 2 and min_mae <= 20:
        return "adjacent_or_near_identical", "medium", "Small filename-ID distance and low resized RGB difference."
    if min_distance <= 4 and min_mae <= 35:
        return "adjacent_or_near_identical", "medium", "Close filename IDs and moderate visual RGB similarity."
    if min_distance <= 2 or pair_count > 10:
        return "uncertain", "medium", "Close filename IDs or large cluster; visual human confirmation is needed."
    if min_mae <= 55:
        return "uncertain", "low", "Some visual similarity is present but not enough for an automated near-identical label."
    return "same_scene_distinct_observation", "low", "Filename proximity remains diagnostic, but selected RGB views look more distinct under automated triage."


def priority_for_label(label, confidence, min_distance, pair_count):
    if label in {"exact_duplicate", "adjacent_or_near_identical"}:
        return 1
    if label == "uncertain":
        return 1 if min_distance <= 2 or pair_count > 10 else 2
    if min_distance <= 2:
        return 2
    return 3


def input_sources():
    return [
        ("v39_train_manifest", TRAIN_MANIFEST),
        ("v39_validation_manifest", VAL_MANIFEST),
        ("filename_proximity_pairs", FILENAME_PAIRS),
        ("uncovered_filename_proximity_pairs", UNCOVERED_PAIRS),
        ("uncovered_filename_proximity_clusters", UNCOVERED_CLUSTERS),
        ("audit_scope_human_review_shortlist", AUDIT_SHORTLIST),
        ("v39_audit_scope_resolution_md", AUDIT_DECISION_MD),
        ("v39_audit_scope_resolution_json", AUDIT_DECISION_JSON),
        ("original_candidate_graph_component_nodes", COMPONENT_NODES),
        ("original_candidate_graph_component_edges", COMPONENT_EDGES),
        ("original_candidate_graph_components", COMPONENTS),
        ("reviewed_41_component_assignment", REVIEWED_41_ASSIGNMENT),
        ("locked_rgb_hashes", RGB_HASHES),
    ]


def snapshot_inputs():
    snapshot_dir = OUT_ROOT / "input_snapshot"
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for label, src in input_sources():
        exists = src.exists()
        snapshot_path = "NA"
        size = "NA"
        digest = "NA"
        if exists:
            digest = sha256_file(src)
            size = src.stat().st_size
            dst = snapshot_dir / f"{label}__{safe_name(src.name)}"
            shutil.copy2(src, dst)
            snapshot_path = repo_rel(dst)
        rows.append(
            {
                "label": label,
                "source_path": repo_rel(src),
                "snapshot_path": snapshot_path,
                "exists": "yes" if exists else "no",
                "size_bytes": size,
                "sha256": digest,
                "copied_at": now_iso(),
                "git_commit": git_commit(),
            }
        )
    commit_path = snapshot_dir / "git_commit.txt"
    commit_path.write_text(git_commit() + "\n", encoding="utf-8")
    rows.append(
        {
            "label": "current_git_commit",
            "source_path": "git rev-parse HEAD",
            "snapshot_path": repo_rel(commit_path),
            "exists": "yes",
            "size_bytes": commit_path.stat().st_size,
            "sha256": sha256_file(commit_path),
            "copied_at": now_iso(),
            "git_commit": git_commit(),
        }
    )
    fields = [
        "label",
        "source_path",
        "snapshot_path",
        "exists",
        "size_bytes",
        "sha256",
        "copied_at",
        "git_commit",
    ]
    write_csv(snapshot_dir / "input_lock_manifest.csv", rows, fields)
    lines = [
        "# V39 Filename-Proximity Review Packet Input Lock",
        "",
        f"- Generated: {now_iso()}",
        f"- Git commit: `{git_commit()}`",
        "- Scope: review packet for filename-proximity diagnostic clusters only.",
        "- Filename numeric ID is a diagnostic proxy only, not verified capture-session metadata.",
        "",
        "| Label | Exists | SHA-256 | Source | Snapshot |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            f"| {row['label']} | {row['exists']} | `{row['sha256']}` | `{row['source_path']}` | `{row['snapshot_path']}` |"
        )
    (snapshot_dir / "input_lock.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return rows


def load_edge_set():
    edges = set()
    for row in read_csv(COMPONENT_EDGES):
        edges.add(tuple(sorted([row["sample_id_a"], row["sample_id_b"]])))
    return edges


def load_rgb_hashes():
    return {row["sample_id"]: row["rgb_pixel_sha256"] for row in read_csv(RGB_HASHES)}


def enrich_pairs(pairs, edge_set, rgb_hashes):
    enriched = []
    for row in pairs:
        out = dict(row)
        out.update(pair_relation_fields(row, edge_set))
        out.update(
            image_similarity_stats(
                out["nearest_train_relative_path"],
                out["validation_relative_path"],
                rgb_hashes,
            )
        )
        enriched.append(out)
    return enriched


def relation_counts(rows):
    return {
        "pair_is_original_candidate_graph_edge": sum(1 for r in rows if r["pair_is_original_candidate_graph_edge"] == "yes"),
        "endpoints_in_same_reviewed_component": sum(1 for r in rows if r["endpoints_in_same_reviewed_component"] == "yes"),
        "one_or_more_endpoint_in_reviewed_component": sum(1 for r in rows if r["one_or_more_endpoint_in_reviewed_component"] == "yes"),
        "neither_endpoint_in_reviewed_component": sum(1 for r in rows if r["neither_endpoint_in_reviewed_component"] == "yes"),
    }


PAIR_FIELDS = [
    "cluster_id",
    "cluster_pair_order",
    "pair_id",
    "family",
    "validation_sample_id",
    "validation_relative_path",
    "validation_numeric_id",
    "nearest_train_sample_id",
    "nearest_train_relative_path",
    "train_numeric_id",
    "id_distance",
    "pair_is_original_candidate_graph_edge",
    "endpoints_in_same_reviewed_component",
    "one_or_more_endpoint_in_reviewed_component",
    "neither_endpoint_in_reviewed_component",
    "validation_cdc_component_id",
    "train_cdc_component_id",
    "validation_reviewed_41_component_ids",
    "train_reviewed_41_component_ids",
    "exact_decoded_rgb_match",
    "resized_rgb_mae",
    "resized_rgb_absdiff_p95",
    "diagnostic_rule",
    "capture_order_claim",
    "selection_basis",
]


def build_packet():
    for rel_dir in [
        "input_snapshot",
        "manifests/clusters",
        "cluster_overviews",
        "pair_reviews",
        "reviewer_forms",
        "codex_preliminary_review",
        "html_index",
        "reports",
        "scripts",
    ]:
        (OUT_ROOT / rel_dir).mkdir(parents=True, exist_ok=True)

    snapshot_rows = snapshot_inputs()
    clusters = {row["cluster_id"]: row for row in read_csv(UNCOVERED_CLUSTERS)}
    pairs = read_csv(UNCOVERED_PAIRS)
    edge_set = load_edge_set()
    rgb_hashes = load_rgb_hashes()
    enriched_pairs = enrich_pairs(pairs, edge_set, rgb_hashes)
    pairs_by_cluster = defaultdict(list)
    for row in enriched_pairs:
        pairs_by_cluster[row["cluster_id"]].append(row)
    for cid in pairs_by_cluster:
        pairs_by_cluster[cid].sort(key=lambda r: (int(r["id_distance"]), r["pair_id"], r["validation_sample_id"], r["nearest_train_sample_id"]))

    cluster_manifest_rows = []
    selected_pair_rows = []
    author_rows = []
    codex_rows = []
    review_asset_rows = []
    overview_paths = []

    for cluster_id in sorted(clusters, key=lambda c: int(c.split("_")[1])):
        cluster = clusters[cluster_id]
        cluster_pairs = pairs_by_cluster[cluster_id]
        if len(cluster_pairs) <= PAIR_SELECT_LIMIT:
            selected = list(cluster_pairs)
            selection_rule = "all pairs selected because cluster pair_count <= 10"
        else:
            selected = list(cluster_pairs[:PAIR_SELECT_LIMIT])
            selection_rule = "first 10 pairs by ascending ID distance and lexical pair ID"
        selected_pair_ids = [r["pair_id"] for r in selected]
        overview_path = OUT_ROOT / "cluster_overviews" / f"{cluster_id}_overview.png"
        pair_pdf_path = OUT_ROOT / "pair_reviews" / f"{cluster_id}_pair_review.pdf"
        make_overview(cluster_id, selected, overview_path)
        make_pair_review_pdf(cluster_id, selected, pair_pdf_path)
        overview_paths.append(overview_path)

        rel_counts = relation_counts(cluster_pairs)
        selected_rel_counts = relation_counts(selected)
        preliminary_label, confidence, rationale = preliminary_label_for_cluster(selected)
        min_distance = min(int(r["id_distance"]) for r in cluster_pairs)
        min_mae = min(float(r["resized_rgb_mae"]) for r in selected)
        priority = priority_for_label(preliminary_label, confidence, min_distance, len(cluster_pairs))
        high_priority = "yes" if priority == 1 else "no"

        cluster_manifest = {
            "cluster_id": cluster_id,
            "family": cluster["family"],
            "pair_count": cluster["pair_count"],
            "node_count": cluster["node_count"],
            "validation_node_count": cluster["validation_node_count"],
            "train_node_count": cluster["train_node_count"],
            "minimum_id_distance": str(min_distance),
            "lexical_min_sample_id": cluster["lexical_min_sample_id"],
            "selected_pair_count": str(len(selected)),
            "selected_pair_ids": "|".join(selected_pair_ids),
            "selection_rule": selection_rule,
            "pair_is_original_candidate_graph_edge_count": str(rel_counts["pair_is_original_candidate_graph_edge"]),
            "endpoints_in_same_reviewed_component_count": str(rel_counts["endpoints_in_same_reviewed_component"]),
            "one_or_more_endpoint_in_reviewed_component_count": str(rel_counts["one_or_more_endpoint_in_reviewed_component"]),
            "neither_endpoint_in_reviewed_component_count": str(rel_counts["neither_endpoint_in_reviewed_component"]),
            "selected_pair_is_original_candidate_graph_edge_count": str(selected_rel_counts["pair_is_original_candidate_graph_edge"]),
            "selected_endpoints_in_same_reviewed_component_count": str(selected_rel_counts["endpoints_in_same_reviewed_component"]),
            "selected_one_or_more_endpoint_in_reviewed_component_count": str(selected_rel_counts["one_or_more_endpoint_in_reviewed_component"]),
            "selected_neither_endpoint_in_reviewed_component_count": str(selected_rel_counts["neither_endpoint_in_reviewed_component"]),
            "preliminary_label": preliminary_label,
            "codex_confidence": confidence,
            "human_review_priority": str(priority),
            "high_priority": high_priority,
            "requires_human_confirmation": "YES",
            "preliminary_automated_triage_only": "YES",
            "minimum_selected_resized_rgb_mae": f"{min_mae:.6f}",
            "overview_png": repo_rel(overview_path),
            "pair_review_pdf": repo_rel(pair_pdf_path),
        }
        cluster_manifest_rows.append(cluster_manifest)
        write_json(OUT_ROOT / "manifests" / "clusters" / f"{cluster_id}.json", cluster_manifest)
        write_csv(
            OUT_ROOT / "manifests" / "clusters" / f"{cluster_id}_selected_pairs.csv",
            selected,
            PAIR_FIELDS,
        )
        for row in selected:
            out = dict(row)
            out["selection_rule"] = selection_rule
            selected_pair_rows.append(out)
        author_rows.append(
            {
                "cluster_id": cluster_id,
                "preliminary_label": preliminary_label,
                "author_final_label": "",
                "author_notes": "",
                "reviewed_by": "",
                "review_date": "",
                "requires_human_confirmation": "YES",
                "representative_pair_ids": "|".join(selected_pair_ids),
                "minimum_id_distance": str(min_distance),
                "pair_count": cluster["pair_count"],
                "allowed_final_labels": "|".join(VALID_FINAL_LABELS),
                "cluster_overview_png": repo_rel(overview_path),
                "pair_review_pdf": repo_rel(pair_pdf_path),
            }
        )
        codex_rows.append(
            {
                "cluster_id": cluster_id,
                "preliminary_label": preliminary_label,
                "codex_confidence": confidence,
                "human_review_priority": str(priority),
                "high_priority": high_priority,
                "requires_human_confirmation": "YES",
                "preliminary_automated_triage_only": "YES",
                "representative_pair_ids": "|".join(selected_pair_ids),
                "minimum_id_distance": str(min_distance),
                "pair_count": cluster["pair_count"],
                "minimum_selected_resized_rgb_mae": f"{min_mae:.6f}",
                "rationale": rationale,
                "overview_png": repo_rel(overview_path),
                "pair_review_pdf": repo_rel(pair_pdf_path),
            }
        )
        review_asset_rows.append(
            {
                "cluster_id": cluster_id,
                "asset_type": "cluster_overview_png",
                "path": repo_rel(overview_path),
                "sha256": sha256_file(overview_path),
                "size_bytes": overview_path.stat().st_size,
            }
        )
        review_asset_rows.append(
            {
                "cluster_id": cluster_id,
                "asset_type": "pair_review_pdf",
                "path": repo_rel(pair_pdf_path),
                "sha256": sha256_file(pair_pdf_path),
                "size_bytes": pair_pdf_path.stat().st_size,
            }
        )

    cluster_fields = [
        "cluster_id",
        "family",
        "pair_count",
        "node_count",
        "validation_node_count",
        "train_node_count",
        "minimum_id_distance",
        "lexical_min_sample_id",
        "selected_pair_count",
        "selected_pair_ids",
        "selection_rule",
        "pair_is_original_candidate_graph_edge_count",
        "endpoints_in_same_reviewed_component_count",
        "one_or_more_endpoint_in_reviewed_component_count",
        "neither_endpoint_in_reviewed_component_count",
        "selected_pair_is_original_candidate_graph_edge_count",
        "selected_endpoints_in_same_reviewed_component_count",
        "selected_one_or_more_endpoint_in_reviewed_component_count",
        "selected_neither_endpoint_in_reviewed_component_count",
        "preliminary_label",
        "codex_confidence",
        "human_review_priority",
        "high_priority",
        "requires_human_confirmation",
        "preliminary_automated_triage_only",
        "minimum_selected_resized_rgb_mae",
        "overview_png",
        "pair_review_pdf",
    ]
    write_csv(OUT_ROOT / "manifests" / "cluster_manifest.csv", cluster_manifest_rows, cluster_fields)
    write_csv(OUT_ROOT / "manifests" / "selected_pair_manifest.csv", selected_pair_rows, PAIR_FIELDS + ["selection_rule"])
    write_csv(
        OUT_ROOT / "manifests" / "all_pair_manifest.csv",
        enriched_pairs,
        PAIR_FIELDS,
    )
    write_csv(
        OUT_ROOT / "manifests" / "review_asset_manifest.csv",
        review_asset_rows,
        ["cluster_id", "asset_type", "path", "sha256", "size_bytes"],
    )
    write_csv(
        OUT_ROOT / "reviewer_forms" / "filename_proximity_author_review.csv",
        author_rows,
        [
            "cluster_id",
            "preliminary_label",
            "author_final_label",
            "author_notes",
            "reviewed_by",
            "review_date",
            "requires_human_confirmation",
            "representative_pair_ids",
            "minimum_id_distance",
            "pair_count",
            "allowed_final_labels",
            "cluster_overview_png",
            "pair_review_pdf",
        ],
    )
    write_csv(
        OUT_ROOT / "codex_preliminary_review" / "codex_preliminary_labels.csv",
        codex_rows,
        [
            "cluster_id",
            "preliminary_label",
            "codex_confidence",
            "human_review_priority",
            "high_priority",
            "requires_human_confirmation",
            "preliminary_automated_triage_only",
            "representative_pair_ids",
            "minimum_id_distance",
            "pair_count",
            "minimum_selected_resized_rgb_mae",
            "rationale",
            "overview_png",
            "pair_review_pdf",
        ],
    )
    shortlist_rows = sorted(codex_rows, key=lambda r: (int(r["human_review_priority"]), int(r["minimum_id_distance"]), r["cluster_id"]))
    write_csv(
        OUT_ROOT / "codex_preliminary_review" / "human_review_shortlist.csv",
        shortlist_rows,
        [
            "cluster_id",
            "preliminary_label",
            "codex_confidence",
            "human_review_priority",
            "high_priority",
            "requires_human_confirmation",
            "preliminary_automated_triage_only",
            "representative_pair_ids",
            "minimum_id_distance",
            "pair_count",
            "minimum_selected_resized_rgb_mae",
            "rationale",
            "overview_png",
            "pair_review_pdf",
        ],
    )

    make_overview_packet_pdf(overview_paths, OUT_ROOT / "reports" / "v39_filename_proximity_human_review_packet.pdf")
    write_html_index(cluster_manifest_rows, codex_rows)
    write_codex_markdown(codex_rows)
    summary = write_reports(snapshot_rows, cluster_manifest_rows, enriched_pairs, selected_pair_rows, codex_rows)
    return summary


def write_html_index(cluster_manifest_rows, codex_rows):
    label_by_cluster = {r["cluster_id"]: r for r in codex_rows}
    rows = []
    for row in cluster_manifest_rows:
        label = label_by_cluster[row["cluster_id"]]
        overview = "../" + row["overview_png"].split("v39_filename_proximity_review_packet_v1/", 1)[-1]
        pair_pdf = "../" + row["pair_review_pdf"].split("v39_filename_proximity_review_packet_v1/", 1)[-1]
        rows.append(
            "<tr>"
            f"<td>{html.escape(row['cluster_id'])}</td>"
            f"<td>{html.escape(row['family'])}</td>"
            f"<td>{html.escape(row['pair_count'])}</td>"
            f"<td>{html.escape(row['minimum_id_distance'])}</td>"
            f"<td>{html.escape(label['preliminary_label'])}</td>"
            f"<td>{html.escape(label['human_review_priority'])}</td>"
            f"<td><a href='{html.escape(overview)}'>overview PNG</a></td>"
            f"<td><a href='{html.escape(pair_pdf)}'>pair-review PDF</a></td>"
            "</tr>"
        )
    doc = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>V39 Filename-Proximity Review Packet</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; color: #111; }}
    table {{ border-collapse: collapse; width: 100%; font-size: 13px; }}
    th, td {{ border: 1px solid #ccc; padding: 6px 8px; text-align: left; }}
    th {{ background: #f2f2f2; position: sticky; top: 0; }}
    .note {{ max-width: 980px; line-height: 1.45; }}
  </style>
</head>
<body>
  <h1>V39 Filename-Proximity Review Packet</h1>
  <p class="note">Filename numeric ID proximity is a diagnostic proxy only. It is not verified capture-session metadata and is not a leakage proof. All preliminary labels require human confirmation. No model output, labels, AP, loss, confidence, or annotation counts are used for prioritization.</p>
  <p><a href="../reviewer_forms/filename_proximity_author_review.csv">Author review CSV</a> | <a href="../reports/v39_filename_proximity_human_review_packet.pdf">Printable overview packet</a></p>
  <table>
    <thead>
      <tr><th>Cluster</th><th>Family</th><th>Pairs</th><th>Min ID Distance</th><th>Preliminary Label</th><th>Priority</th><th>Overview</th><th>Pair PDF</th></tr>
    </thead>
    <tbody>
      {''.join(rows)}
    </tbody>
  </table>
</body>
</html>
"""
    (OUT_ROOT / "html_index" / "index.html").write_text(doc, encoding="utf-8")
    shutil.copy2(OUT_ROOT / "html_index" / "index.html", OUT_ROOT / "codex_preliminary_review" / "codex_review_dashboard.html")


def write_codex_markdown(codex_rows):
    counts = Counter(r["preliminary_label"] for r in codex_rows)
    priority_counts = Counter(r["human_review_priority"] for r in codex_rows)
    lines = [
        "# Codex Preliminary Filename-Proximity Review",
        "",
        f"- Generated: {now_iso()}",
        "- Scope: preliminary automated visual triage for all 70 clusters.",
        "- `preliminary_automated_triage_only=YES` and `requires_human_confirmation=YES` for every row.",
        "- Filename numeric ID is a diagnostic proxy only, not verified capture-session metadata.",
        "- No model output, labels, AP, loss, confidence, or annotation counts were used.",
        "",
        "## Preliminary Label Counts",
        "",
        "| Label | Count |",
        "| --- | ---: |",
    ]
    for label in VALID_FINAL_LABELS:
        lines.append(f"| {label} | {counts[label]} |")
    lines.extend(
        [
            "",
            "## Priority Counts",
            "",
            "| Priority | Count |",
            "| --- | ---: |",
        ]
    )
    for priority in sorted(priority_counts, key=int):
        lines.append(f"| {priority} | {priority_counts[priority]} |")
    lines.extend(
        [
            "",
            "## Cluster Rows",
            "",
            "| Cluster | Preliminary Label | Priority | Representative Pair IDs | Rationale |",
            "| --- | --- | ---: | --- | --- |",
        ]
    )
    for row in codex_rows:
        lines.append(
            f"| {row['cluster_id']} | {row['preliminary_label']} | {row['human_review_priority']} | "
            f"{row['representative_pair_ids']} | {row['rationale']} |"
        )
    (OUT_ROOT / "codex_preliminary_review" / "codex_preliminary_review.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )


def write_reports(snapshot_rows, cluster_rows, all_pairs, selected_pairs, codex_rows):
    label_counts = Counter(r["preliminary_label"] for r in codex_rows)
    priority_counts = Counter(r["human_review_priority"] for r in codex_rows)
    high_priority_count = sum(1 for r in codex_rows if r["high_priority"] == "yes")
    source_lock_status = "PASS" if all(r["exists"] == "yes" for r in snapshot_rows) else "MISSING_INPUT"
    summary = {
        "generated_at": now_iso(),
        "git_commit": git_commit(),
        "total_cluster_count": len(cluster_rows),
        "total_pair_count": len(all_pairs),
        "selected_pair_count": len(selected_pairs),
        "preliminary_label_counts": dict(label_counts),
        "priority_counts": dict(priority_counts),
        "clusters_marked_high_priority": high_priority_count,
        "source_lock_status": source_lock_status,
        "author_review_csv": repo_rel(OUT_ROOT / "reviewer_forms" / "filename_proximity_author_review.csv"),
        "html_index": repo_rel(OUT_ROOT / "html_index" / "index.html"),
        "print_packet_pdf": repo_rel(OUT_ROOT / "reports" / "v39_filename_proximity_human_review_packet.pdf"),
        "pair_review_pdf_count": len(cluster_rows),
        "cluster_overview_png_count": len(cluster_rows),
        "training_started": False,
        "split_changed": False,
        "manuscript_changed": False,
        "model_changed": False,
        "evaluator_changed": False,
        "raw_data_changed": False,
        "guard_partition_changed": False,
        "filename_proximity_statement": "Filename numeric ID proximity is a diagnostic proxy only; it is not verified capture-session metadata and does not prove temporal leakage by itself.",
    }
    write_json(OUT_ROOT / "reports" / "v39_filename_proximity_review_packet_summary.json", summary)
    lines = [
        "# V39 Filename-Proximity Review Packet Summary",
        "",
        f"- Generated: {summary['generated_at']}",
        f"- Git commit: `{summary['git_commit']}`",
        f"- Source-lock status: `{source_lock_status}`",
        f"- Total clusters: {summary['total_cluster_count']}",
        f"- Total filename-proximity pairs: {summary['total_pair_count']}",
        f"- Selected representative pairs in PDFs: {summary['selected_pair_count']}",
        f"- Clusters marked high priority: {summary['clusters_marked_high_priority']}",
        "",
        "Filename numeric ID proximity is a diagnostic proxy only; it is not verified capture-session metadata and does not prove temporal leakage by itself.",
        "",
        "## Preliminary Label Counts",
        "",
        "| Label | Count |",
        "| --- | ---: |",
    ]
    for label in VALID_FINAL_LABELS:
        lines.append(f"| {label} | {label_counts[label]} |")
    lines.extend(
        [
            "",
            "## Review Paths",
            "",
            f"- Author review CSV: `{summary['author_review_csv']}`",
            f"- HTML index: `{summary['html_index']}`",
            f"- Printable overview packet: `{summary['print_packet_pdf']}`",
            "- Per-cluster overview PNGs: `cluster_overviews/`.",
            "- Per-cluster pair-review PDFs: `pair_reviews/`.",
            "",
            "## Safeguards",
            "",
            "- No p=0.20 training was started.",
            "- No split, guard definition, model, evaluator, raw data, label, manuscript, existing V39 result, checkpoint, AP, loss, confidence, or prediction output was changed or used for prioritization.",
            "- The author review form leaves `author_final_label`, `reviewed_by`, and `review_date` blank.",
            "- Every Codex preliminary row has `preliminary_automated_triage_only=YES` and `requires_human_confirmation=YES`.",
        ]
    )
    (OUT_ROOT / "reports" / "v39_filename_proximity_review_packet_summary.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )
    return summary


def main():
    summary = build_packet()
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
