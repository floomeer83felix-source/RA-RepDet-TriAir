"""CPU-only final provider and alignment audit for the frozen V52 MM-UAV subset."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "runs" / "v52_mmuav_audit"
MANIFESTS = OUT / "manifests"
DATA_ROOT = Path(r"E:\MM-UAV_extracted\MMMUAV\train")
BENCHMARK = Path(r"D:\MM-UAV_provider_audit\Benchmark")
EVALUATION = Path(r"D:\MM-UAV_provider_audit\Evaluation")
PAPER = Path(r"D:\MM-UAV_provider_audit\arxiv_2511.18344v3.html")
START_COMMIT = "895a09753f84a3883a709d587c3a852ace8af0c4"
BENCHMARK_COMMIT = "5051e4451a2b66dba9128fb0f766832152e7d120"
EVALUATION_COMMIT = "a468fb66db9e67c00357e1bd3f169745c389bab7"
PAPER_SHA256 = "89e69fb5865b530a2e04bd14cf0b20833e4bf8956b1f9b666db3bd2920fb0822"
NOW = datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(name: str, value: object) -> None:
    (OUT / name).write_text(json.dumps(value, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def write_csv(name: str, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    with (OUT / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def git_output(*args: str, cwd: Path = ROOT) -> str:
    return subprocess.check_output(["git", *args], cwd=cwd, text=True).strip()


def gt_index(path: Path, cache: dict[Path, dict[int, set[int]]]) -> dict[int, set[int]]:
    if path in cache:
        return cache[path]
    frames: dict[int, set[int]] = defaultdict(set)
    with path.open(encoding="utf-8", newline="") as handle:
        for row in csv.reader(handle):
            if len(row) >= 2:
                frames[int(float(row[0]))].add(int(float(row[1])))
    cache[path] = frames
    return frames


def reproduce_annotated_only() -> tuple[list[dict[str, object]], list[dict[str, str]]]:
    cache: dict[Path, dict[int, set[int]]] = {}
    records: list[dict[str, object]] = []
    derivative: list[dict[str, str]] = []
    status_sequences: dict[tuple[str, str], set[str]] = defaultdict(set)
    status_samples: dict[tuple[str, str], int] = defaultdict(int)
    statuses = ("RGB_GT_PRESENT", "IR_GT_PRESENT", "BOTH_GT_PRESENT", "RGB_ONLY_GT_PRESENT",
                "IR_ONLY_GT_PRESENT", "NEITHER_GT_PRESENT", "ANY_SOURCE_GT_PRESENT",
                "COMMON_TRACK_ID_PRESENT")

    for split in ("train", "devval"):
        path = MANIFESTS / f"{split}_sampled.txt"
        with path.open(encoding="utf-8", newline="") as handle:
            for ordinal, row in enumerate(csv.DictReader(handle, delimiter="\t"), start=1):
                rgb_present = int(row["rgb_annotation_rows"]) > 0
                ir_present = int(row["ir_annotation_rows"]) > 0
                frame = int(row["frame_index"])
                common_ids = gt_index(Path(row["gt_rgb"]), cache).get(frame, set()) & gt_index(
                    Path(row["gt_ir"]), cache
                ).get(frame, set())
                flags = {
                    "RGB_GT_PRESENT": rgb_present,
                    "IR_GT_PRESENT": ir_present,
                    "BOTH_GT_PRESENT": rgb_present and ir_present,
                    "RGB_ONLY_GT_PRESENT": rgb_present and not ir_present,
                    "IR_ONLY_GT_PRESENT": ir_present and not rgb_present,
                    "NEITHER_GT_PRESENT": not rgb_present and not ir_present,
                    "ANY_SOURCE_GT_PRESENT": rgb_present or ir_present,
                    "COMMON_TRACK_ID_PRESENT": bool(common_ids),
                }
                for status, enabled in flags.items():
                    if enabled:
                        status_samples[(split, status)] += 1
                        status_sequences[(split, status)].add(row["sequence"])
                if flags["ANY_SOURCE_GT_PRESENT"]:
                    traced = {
                        "original_row_id": f"{split}:{ordinal:08d}",
                        "split": split,
                        **row,
                        "audited_annotation_state": "SOURCE_GT_ROW_PRESENT",
                        "common_track_ids": ";".join(map(str, sorted(common_ids))),
                    }
                    derivative.append(traced)

    for scope in ("train", "devval", "total"):
        for status in statuses:
            if scope == "total":
                sample_count = sum(status_samples[(split, status)] for split in ("train", "devval"))
                sequence_count = len(status_sequences[("train", status)] | status_sequences[("devval", status)])
            else:
                sample_count = status_samples[(scope, status)]
                sequence_count = len(status_sequences[(scope, status)])
            records.append({"scope": scope, "status": status, "sample_count": sample_count,
                            "sequence_count": sequence_count})

    included = next(r["sample_count"] for r in records if r["scope"] == "total" and r["status"] == "ANY_SOURCE_GT_PRESENT")
    excluded = next(r["sample_count"] for r in records if r["scope"] == "total" and r["status"] == "NEITHER_GT_PRESENT")
    if (included, excluded) != (9138, 35898):
        raise RuntimeError(f"annotated-only contract mismatch: included={included}, excluded={excluded}")

    derivative_path = MANIFESTS / "annotated_only_sampled.txt"
    with derivative_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(derivative[0]), delimiter="\t")
        writer.writeheader()
        writer.writerows(derivative)
    return records, derivative


def evidence_inventory() -> list[dict[str, object]]:
    converter = BENCHMARK / "tools/datasets/convert_MMMUAV_to_coco.py"
    deform = BENCHMARK / "yolox/models/yolo_pafpn2_def.py"
    stn = BENCHMARK / "yolox/models/yolo_pafpn2_stn.py"
    cmc = BENCHMARK / "VideoCameraCorrection/VideoCameraCorrection/cmc.cpp"
    main = BENCHMARK / "VideoCameraCorrection/VideoCameraCorrection/main.cpp"
    paths = [
        ("official_paper", PAPER, "official arXiv v3", "1286-1304; 1799-1802", "Independent RGB/IR boxes, no event boxes, sparse cadence, learned STN initialization", "explicit"),
        ("official_converter", converter, f"official baseline commit {BENCHMARK_COMMIT}", "38-44; 69-102; 155-236", "Drone category; separate GT; common annotated frame intersection; partial field use", "explicit_code"),
        ("deformable_alignment", deform, f"official baseline commit {BENCHMARK_COMMIT}", "111-130; 163-183", "Learned deformable feature alignment", "explicit_code"),
        ("stn_alignment", stn, f"official baseline commit {BENCHMARK_COMMIT}", "100-108; 110-153; 175-193", "Global affine initialization plus trainable feature-level delta", "explicit_code"),
        ("temporal_cmc", cmc, f"official baseline commit {BENCHMARK_COMMIT}", "14-77", "Within-video temporal camera-motion correction, not cross-modal registration", "explicit_code"),
        ("temporal_cmc_entry", main, f"official baseline commit {BENCHMARK_COMMIT}", "relevant program body", "Writes per-frame temporal GMC", "explicit_code"),
        ("baseline_readme", BENCHMARK / "README.md", f"official baseline commit {BENCHMARK_COMMIT}", "dataset and baseline sections", "Official repository and feature-alignment baseline", "explicit"),
        ("baseline_code_license", BENCHMARK / "LICENSE", f"official baseline commit {BENCHMARK_COMMIT}", "full file", "Apache-2.0 covers repository code, not expressly dataset files", "explicit"),
        ("evaluation_readme", EVALUATION / "README.md", f"official evaluation commit {EVALUATION_COMMIT}", "full file", "Official evaluation instructions; no spatial calibration contract", "explicit"),
        ("evaluation_code_license", EVALUATION / "LICENSE", f"official evaluation commit {EVALUATION_COMMIT}", "full file", "Repository code license; not a dataset license", "explicit"),
        ("local_seqinfo_rgb", DATA_ROOT / "0007/seqinfo-rgb.ini", "provider dataset file", "all keys", "Native RGB dimensions and frame metadata", "explicit_file"),
        ("local_seqinfo_ir", DATA_ROOT / "0007/seqinfo-ir.ini", "provider dataset file", "all keys", "Native IR dimensions and frame metadata", "explicit_file"),
        ("local_gt_rgb", DATA_ROOT / "0007/gt_rgb/gt.txt", "provider dataset file", "9-column rows", "Sparse RGB annotations; column values alone do not define semantics", "explicit_file"),
        ("local_gt_ir", DATA_ROOT / "0007/gt_ir/gt.txt", "provider dataset file", "9-column rows", "Sparse IR annotations; column values alone do not define semantics", "explicit_file"),
    ]
    result = []
    for artifact_id, path, source, location, claim, evidence_type in paths:
        if not path.is_file():
            raise FileNotFoundError(path)
        result.append({
            "artifact_id": artifact_id,
            "path_or_url": str(path),
            "sha256": sha256(path),
            "source": source,
            "provider_controlled": True,
            "relevant_location": location,
            "claim_supported": claim,
            "evidence_classification": evidence_type,
            "retrieved_at": NOW,
        })
    if result[0]["sha256"] != PAPER_SHA256:
        raise RuntimeError("official paper hash changed")
    return result


def inventory_downloads() -> dict[str, object]:
    rows: list[dict[str, object]] = []
    for source, repo, commit in (("official_baseline", BENCHMARK, BENCHMARK_COMMIT),
                                 ("official_evaluation", EVALUATION, EVALUATION_COMMIT)):
        for relative in git_output("ls-files", cwd=repo).splitlines():
            path = repo / relative
            if path.is_file():
                rows.append({"source": source, "pinned_commit": commit, "relative_path": relative,
                             "absolute_path": str(path), "bytes": path.stat().st_size, "sha256": sha256(path)})
    rows.append({"source": "official_arxiv_v3", "pinned_commit": "2511.18344v3",
                 "relative_path": PAPER.name, "absolute_path": str(PAPER), "bytes": PAPER.stat().st_size,
                 "sha256": sha256(PAPER)})
    write_csv("provider_download_inventory.csv", list(rows[0]), rows)
    material_bytes = sum(p.stat().st_size for root in (BENCHMARK, EVALUATION) for p in root.rglob("*") if p.is_file()) + PAPER.stat().st_size
    return {"inventoried_files": len(rows), "tracked_worktree_bytes": sum(int(r["bytes"]) for r in rows),
            "total_downloaded_material_bytes_including_git": material_bytes, "limit_bytes": 1_000_000_000,
            "below_limit": material_bytes < 1_000_000_000}


def search_local_provider_files() -> dict[str, object]:
    terms = ("align", "alignment", "registration", "calibration", "calibrate", "homography", "affine",
             "warp", "rectify", "rectification", "intrinsic", "extrinsic", "distortion", "transform",
             "coordinate", "crop", "resize", "pad", "roi", "timestamp", "sync", "annotation",
             "visibility", "occlusion", "truncation", "confidence", "class", "category", "license")
    searched: list[Path] = []
    matches: list[dict[str, object]] = []
    for sequence in sorted(p for p in DATA_ROOT.iterdir() if p.is_dir()):
        candidates = list(sequence.glob("*.*"))
        for subdir in ("gt_rgb", "gt_ir", "sot_groundtruth"):
            folder = sequence / subdir
            if folder.is_dir():
                candidates.extend(p for p in folder.iterdir() if p.is_file())
        for path in candidates:
            searched.append(path)
            name_hits = sorted(term for term in terms if term in path.name.lower())
            content_hits: list[str] = []
            if path.suffix.lower() in {".ini", ".md", ".txt", ".csv", ".json", ".yaml", ".yml"}:
                text = path.read_text(encoding="utf-8", errors="replace").lower()
                content_hits = sorted(term for term in terms if term in text)
            if name_hits or content_hits:
                matches.append({"path": str(path), "sha256": sha256(path),
                                "filename_terms": ";".join(name_hits), "content_terms": ";".join(content_hits)})
    write_csv("local_provider_search_matches.csv", ["path", "sha256", "filename_terms", "content_terms"], matches)
    return {"provider_nonmedia_files_searched": len(searched), "matching_files": len(matches),
            "terms": list(terms), "media_filename_coverage": "frozen directory inventory and 45,036-row interval-20 manifests",
            "complete_sequences": 424}


def alignment_candidates() -> list[dict[str, object]]:
    return [
        {"candidate": "OGAA deformable convolution", "classification": "LEARNED_FEATURE_ALIGNMENT", "mapping": "RGB<->IR feature maps", "parameter_scope": "per sample learned offsets", "executable_complete": True, "changes_annotations": False, "purpose": "detection feature fusion", "reproducible_without_devval_gt_fit": True},
        {"candidate": "OGAA spatial transformer", "classification": "LEARNED_FEATURE_ALIGNMENT", "mapping": "RGB<->IR feature maps", "parameter_scope": "global fixed initialization plus per-sample learned delta", "executable_complete": True, "changes_annotations": False, "purpose": "detection feature fusion", "reproducible_without_devval_gt_fit": True},
        {"candidate": "STN fixed theta constants alone", "classification": "CALIBRATION_PARAMETERS_ONLY", "mapping": "RGB<->IR feature grids", "parameter_scope": "global", "executable_complete": False, "changes_annotations": False, "purpose": "initialization for learned feature STN", "reproducible_without_devval_gt_fit": False},
        {"candidate": "VideoCameraCorrection GMC", "classification": "FIXED_PREPROCESSING_WITHOUT_CALIBRATION", "mapping": "previous->current frame within one video", "parameter_scope": "per frame estimated from video", "executable_complete": True, "changes_annotations": False, "purpose": "tracking camera-motion compensation", "reproducible_without_devval_gt_fit": True},
        {"candidate": "synchronized frame indices", "classification": "TEMPORAL_SYNCHRONIZATION_ONLY", "mapping": "RGB/IR/event frame index", "parameter_scope": "per frame", "executable_complete": True, "changes_annotations": False, "purpose": "temporal pairing", "reproducible_without_devval_gt_fit": True},
        {"candidate": "independent input resize/letterbox", "classification": "FIXED_PREPROCESSING_WITHOUT_CALIBRATION", "mapping": "each native grid->network feature grid", "parameter_scope": "per modality", "executable_complete": True, "changes_annotations": False, "purpose": "network preprocessing", "reproducible_without_devval_gt_fit": True},
        {"candidate": "expanded event crop for motion embedding", "classification": "FIXED_PREPROCESSING_WITHOUT_CALIBRATION", "mapping": "RGB/IR track box vicinity->event crop", "parameter_scope": "per track/frame", "executable_complete": True, "changes_annotations": False, "purpose": "tracking association feature", "reproducible_without_devval_gt_fit": True},
    ]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    records, derivative = reproduce_annotated_only()
    write_csv("annotated_only_status_counts.csv", ["scope", "status", "sample_count", "sequence_count"], records)
    totals = {r["status"]: r for r in records if r["scope"] == "total"}
    protocol = {
        "generated_at": NOW, "starting_commit": START_COMMIT,
        "predicate": "rgb_annotation_rows > 0 OR ir_annotation_rows > 0",
        "included": 9138, "excluded_unlabeled": 35898, "total": 45036,
        "excluded_state": "UNLABELED", "empty_target_assignments": 0,
        "source_manifests": ["manifests/train_sampled.txt", "manifests/devval_sampled.txt"],
        "derivative_manifest": "manifests/annotated_only_sampled.txt",
        "derivative_sha256": sha256(MANIFESTS / "annotated_only_sampled.txt"),
    }
    write_json("annotated_only_protocol.json", protocol)
    (OUT / "annotated_only_protocol.md").write_text(
        "# V52 Annotated-Only Protocol\n\n"
        "Predicate: `rgb_annotation_rows > 0 OR ir_annotation_rows > 0`. The frozen interval-20 manifests are not changed. "
        "The derivative retains split, original row ID, sequence, source index, every path, row counts, and common IDs.\n\n"
        "Result: **9,138 included; 35,898 excluded as `UNLABELED`; 0 empty-target assignments.**\n",
        encoding="utf-8",
    )
    (OUT / "annotated_only_integrity.md").write_text(
        "# V52 Annotated-Only Integrity\n\n"
        f"- Source rows: 45,036\n- Derivative rows: {len(derivative):,}\n"
        f"- Derivative SHA256: `{protocol['derivative_sha256']}`\n"
        "- Original manifests unchanged: yes\n- Missing-GT rows relabeled as empty targets: no\n"
        "- Exact frozen contract reproduced: yes\n",
        encoding="utf-8",
    )

    evidence = evidence_inventory()
    downloads = inventory_downloads()
    local_search = search_local_provider_files()
    write_csv("provider_evidence_inventory.csv", list(evidence[0]), evidence)
    provider = {
        "generated_at": NOW, "official_sources_accessible": True,
        "official_commits": {"benchmark": BENCHMARK_COMMIT, "evaluation": EVALUATION_COMMIT},
        "paper": {"url": "https://arxiv.org/html/2511.18344v3", "sha256": PAPER_SHA256},
        "local_search": {"root": str(DATA_ROOT), **local_search},
        "download_inventory": downloads,
        "findings": ["Provider paper defines sparse train cadence as every 100 frames.",
                     "Official converter trains only on the intersection of RGB/IR annotated frame IDs.",
                     "No provider dataset file supplies raw-grid calibration or explicit dataset-use license."],
        "evidence_count": len(evidence),
    }
    write_json("provider_contract_audit.json", provider)
    (OUT / "provider_contract_audit.md").write_text(
        "# V52 Provider Contract Audit\n\n"
        f"Official baseline `{BENCHMARK_COMMIT}` and evaluation `{EVALUATION_COMMIT}` were pinned. "
        f"The official arXiv v3 HTML hash is `{PAPER_SHA256}`.\n\n"
        "Every tracked file in both pinned official clones and the paper HTML is hashed in `provider_download_inventory.csv`; total material remains below 1 GB. "
        "All provider non-media files in 424 extracted sequences were searched by filename and text, with matches recorded in `local_provider_search_matches.csv`. "
        "The paper explicitly states independent RGB/IR annotation, no event boxes, and sparse training annotation every 100 frames. "
        "The official converter intersects RGB/IR annotated frame IDs and therefore excludes unannotated frames. "
        "No searched provider artifact defines missing rows as verified empty scenes, supplies a complete raw-grid calibration recipe, "
        "fully defines all final MOT-like fields, or grants a dataset license. See `provider_evidence_inventory.csv`.\n",
        encoding="utf-8",
    )

    candidates = alignment_candidates()
    write_csv("alignment_candidate_inventory.csv", list(candidates[0]), candidates)
    alignment = {
        "generated_at": NOW, "deterministic_raw_grid_transform_found": False,
        "official_learned_feature_alignment_found": True,
        "classification_guard": "Only PIXEL_SPACE_DETERMINISTIC_TRANSFORM with complete executable inputs may unlock verification.",
        "candidates": candidates,
    }
    write_json("alignment_source_audit.json", alignment)
    (OUT / "alignment_source_audit.md").write_text(
        "# V52 Alignment Source Audit\n\n"
        "Official OGAA uses learned deformable offsets or a trainable feature STN. The published fixed STN matrices are only global "
        "initialization; the provider does not supply the selected source pair, keypoints, detector settings, raw-grid conventions, "
        "annotation transform, or event calibration needed to reproduce a pixel-space registration. Temporal GMC, synchronization, "
        "resizing, and event crop expansion are not spatial calibration.\n\n"
        "**Deterministic RGB/IR/event raw-grid transform: not found.**\n",
        encoding="utf-8",
    )
    verification = {"generated_at": NOW, "status": "NOT_RUN_NO_OFFICIAL_DETERMINISTIC_TRANSFORM",
                    "devval_gt_fitting": False, "reason": "No complete provider-supplied raw-grid transform or calibration recipe."}
    write_json("official_alignment_verification.json", verification)
    write_csv("official_alignment_verification.csv", ["generated_at", "status", "devval_gt_fitting", "reason"],
              [{"generated_at": NOW, **verification}])
    (OUT / "official_alignment_verification.md").write_text(
        "# V52 Official Alignment Verification\n\nStatus: `NOT_RUN_NO_OFFICIAL_DETERMINISTIC_TRANSFORM`. "
        "No substitute transform was fitted, and development-validation GT was not used.\n", encoding="utf-8")

    sparse = {"status": "PARTIALLY_CONFIRMED", "missing_row_meaning": "UNANNOTATED_OR_EMPTY_UNRESOLVED",
              "verified_empty_target": False, "interpolation_expected": "not stated",
              "fixed_cadence": "training sequences every 100 frames; test sequences every 20 frames",
              "operational_converter_behavior": "intersection of RGB and IR annotated frame IDs only",
              "unlabeled_rows_preserved": 35898}
    fields = {"status": "PARTIALLY_CONFIRMED", "category": "drone", "columns_confirmed": ["frame", "track_id", "x", "y", "width", "height"],
              "remaining_fields": "converter uses column 7 as conf/filter and ignores column 9; provider prose does not completely define final three fields"}
    license_contract = {"status": "UNRESOLVED", "dataset_license": None,
                        "code_license": "Apache-2.0 in official repositories",
                        "paper_license": "CC BY-NC-SA 4.0 for arXiv paper; not a dataset grant"}
    for stem, value, text in (
        ("sparse_gt_contract", sparse, "Provider confirms sparse annotation cadence and official code excludes missing frames, but does not define every absent row as a verified empty target or prescribe interpolation."),
        ("category_and_fields_contract", fields, "Official converter confirms category `drone` and the first six MOT-like fields operationally. The final three fields are not completely and consistently defined by provider prose/code comments."),
        ("license_contract", license_contract, "Official code is Apache-2.0 and the arXiv paper has its own content license. No explicit license or research-use grant for the dataset files was found."),
    ):
        write_json(f"{stem}.json", value)
        (OUT / f"{stem}.md").write_text(f"# {stem.replace('_', ' ').title()}\n\nStatus: `{value['status']}`. {text}\n", encoding="utf-8")

    outcome = "OFFICIAL_LEARNED_ALIGNMENT_ONLY_DIRECT_FUSION_NO_GO"
    decision = {"generated_at": NOW, "outcome": outcome, "direct_channel_fusion": "NO_GO",
                "deterministic_spatial_transform": False, "official_learned_feature_alignment": True,
                "annotated_only_included": 9138, "unlabeled_excluded": 35898,
                "sparse_gt_status": sparse["status"], "category_fields_status": fields["status"],
                "dataset_license_status": license_contract["status"], "pilot_locked": True, "gpu_optimizer_steps": 0}
    write_json("feasibility_decision.json", decision)
    (OUT / "feasibility_decision.md").write_text(
        f"# V52 Final Feasibility Decision\n\nOutcome: `{outcome}`.\n\n"
        "Official code addresses RGB/IR mismatch through learned feature alignment, not a reproducible raw-grid registration. "
        "Direct RGB/thermal/event channel concatenation remains invalid. A learned alignment module would be a separate, explicitly authorized method expansion. "
        "The 200-step pilot remains locked.\n", encoding="utf-8")
    (OUT / "claim_boundary.md").write_text(
        "# V52 Claim Boundary\n\nAllowed claim: the frozen local subset reproduces 9,138 source-annotated triplets and 35,898 unlabeled triplets; "
        "official MM-UAV uses learned RGB/IR feature alignment and provides no complete RGB/IR/event raw-grid calibration found by this audit.\n\n"
        "Forbidden claims: unlabeled frames are negatives; modalities are pixel aligned; STN initialization is a raw-pixel calibration; "
        "MM-UAV training or detection metrics were run; dataset reuse is licensed.\n", encoding="utf-8")
    gate_path = OUT / "pilot_gate.json"
    gate = json.loads(gate_path.read_text(encoding="utf-8"))
    gate.update({"locked": True, "gpu_steps": 0, "gpu_optimizer_steps": 0, "audit_outcome": outcome,
                 "updated_at": NOW})
    write_json("pilot_gate.json", gate)

    protected = ["rarepdet/train_early_fusion.py", "rarepdet/models/early_fusion_fcos.py",
                 "rarepdet/models/reliability_fusion_fcos.py", "datasets/triair_dataset.py"]
    changed = set(git_output("diff", "--name-only", START_COMMIT).splitlines())
    manuscript_changed = sorted(p for p in changed if p in {"main.tex", "main_sivp_snjnl.tex"} or p.startswith("manuscript/") or p.startswith("submission/"))
    protected_changed = sorted(set(protected) & changed)
    source_lock = {"starting_commit": START_COMMIT, "protected_core_changed": protected_changed,
                   "manuscript_changed": manuscript_changed, "gpu_optimizer_steps": 0}
    write_json("provider_audit_source_lock.json", source_lock)
    if protected_changed or manuscript_changed:
        raise RuntimeError(f"protected paths changed: {protected_changed + manuscript_changed}")

    print(json.dumps({"included": 9138, "excluded": 35898,
                      "common_track_frames": totals["COMMON_TRACK_ID_PRESENT"]["sample_count"],
                      "outcome": outcome}, indent=2))


if __name__ == "__main__":
    main()
