#!/usr/bin/env python
"""Generate a lightweight handoff report for the RA-RepDet TriAir workspace."""

import csv
import json
import subprocess
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RUNS_DIR = PROJECT_ROOT / "runs"


EXPERIMENTS = [
    {
        "id": "E0",
        "method": "Early Fusion",
        "dir": RUNS_DIR / "E0_early_repvit_fcos_e50",
    },
    {
        "id": "E1",
        "method": "Reliability Fusion",
        "dir": RUNS_DIR / "E1_reliability_repvit_fcos_e50",
    },
    {
        "id": "E2",
        "method": "Reliability + Dropout 0.15",
        "dir": RUNS_DIR / "E2_reliability_dropout015_repvit_fcos_e50",
    },
    {
        "id": "E3",
        "method": "Reliability + Dropout 0.10",
        "dir": RUNS_DIR / "E3_reliability_dropout010_repvit_fcos_e50",
        "eval_subdir": "eval_thr050",
    },
    {
        "id": "E4",
        "method": "Reliability + Dropout 0.20",
        "dir": RUNS_DIR / "E4_reliability_dropout020_repvit_fcos_e50",
        "eval_subdir": "eval_thr050",
    },
    {
        "id": "E5",
        "method": "ACRF + Dropout 0.15",
        "dir": RUNS_DIR / "E5_acrf_dropout015_repvit_fcos_e50",
        "eval_subdir": "eval_thr050",
    },
    {
        "id": "E6",
        "method": "MSCD + Dropout 0.15",
        "dir": RUNS_DIR / "E6_mscd_dropout015_repvit_fcos_e50",
        "eval_subdir": "eval_thr050",
    },
]


def read_pipe_table(path):
    if not path.exists():
        return []
    rows = []
    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not lines:
        return rows
    headers = [part.strip() for part in lines[0].split("|")]
    for line in lines[2:]:
        values = [part.strip() for part in line.split("|")]
        if len(values) == len(headers):
            rows.append(dict(zip(headers, values)))
    return rows


def read_csv(path):
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def count_csv_rows(path):
    if not path.exists():
        return 0
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        next(reader, None)
        return sum(1 for _ in reader)


def read_key_value_file(path):
    if not path.exists():
        return {}
    values = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip()
    return values


def git_lines(args):
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=PROJECT_ROOT,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    except Exception as exc:
        return [f"git unavailable: {exc}"]
    output = (result.stdout or result.stderr).strip()
    return output.splitlines() if output else []


def collect_eval_results():
    results = []
    for exp in EXPERIMENTS:
        eval_subdir = exp.get("eval_subdir", "eval")
        row = read_key_value_file(exp["dir"] / eval_subdir / "eval_results.txt")
        results.append(
            {
                "id": exp["id"],
                "method": exp["method"],
                "precision": row.get("Precision"),
                "recall": row.get("Recall"),
                "ap50": row.get("AP50"),
                "ap75": row.get("AP75"),
                "gt_boxes": row.get("GT boxes"),
                "predictions": row.get("Predictions"),
                "mean_confidence": row.get("Mean Confidence"),
            }
        )
    return results


def collect_missing_modality():
    summary = read_csv(RUNS_DIR / "missing_modality_summary.csv")
    summary_ap75 = read_csv(RUNS_DIR / "missing_modality_summary_ap75.csv")
    return {"ap50": summary, "ap75": summary_ap75}


def collect_profile():
    return read_csv(RUNS_DIR / "profile_summary.csv")


def collect_phase2a():
    return {
        "main_results": read_csv(RUNS_DIR / "phase2a_main_results.csv"),
        "profile_e0": read_csv(RUNS_DIR / "phase2a_profile_e0" / "profile_results.csv"),
        "profile_e2": read_csv(RUNS_DIR / "phase2a_profile_e2" / "profile_results.csv"),
        "brightness_proxy": read_csv(RUNS_DIR / "phase2a_brightness_proxy" / "brightness_proxy_results.csv"),
        "alpha_modes": read_csv(RUNS_DIR / "phase2a_alpha" / "alpha_mode_summary.csv"),
        "report": str(RUNS_DIR / "phase2a_report.md") if (RUNS_DIR / "phase2a_report.md").exists() else None,
    }


def collect_phase2b():
    return {
        "evidence_summary": read_csv(RUNS_DIR / "acrf_evidence_summary.csv"),
        "evidence_report": str(RUNS_DIR / "acrf_evidence_report.md") if (RUNS_DIR / "acrf_evidence_report.md").exists() else None,
        "smoke_test": str(RUNS_DIR / "acrf_smoke_test.md") if (RUNS_DIR / "acrf_smoke_test.md").exists() else None,
        "e5_missing_modality": read_csv(
            RUNS_DIR / "E5_acrf_dropout015_repvit_fcos_e50" / "missing_modality" / "missing_modality_results.csv"
        ),
        "e5_alpha_modes": read_csv(
            RUNS_DIR / "E5_acrf_dropout015_repvit_fcos_e50" / "alpha_modes" / "alpha_mode_summary.csv"
        ),
    }


def collect_phase2c():
    return {
        "evidence_summary": read_csv(RUNS_DIR / "mscd_evidence_summary.csv"),
        "evidence_report": str(RUNS_DIR / "mscd_evidence_report.md") if (RUNS_DIR / "mscd_evidence_report.md").exists() else None,
        "phase2c_report": str(RUNS_DIR / "phase2c_report.md") if (RUNS_DIR / "phase2c_report.md").exists() else None,
        "smoke_test": str(RUNS_DIR / "mscd_smoke_test.md") if (RUNS_DIR / "mscd_smoke_test.md").exists() else None,
        "e6_missing_modality": read_csv(
            RUNS_DIR / "E6_mscd_dropout015_repvit_fcos_e50" / "missing_modality" / "missing_modality_results.csv"
        ),
    }


def collect_phase3a():
    return {
        "dropout_ablation": read_csv(RUNS_DIR / "dropout_ablation_summary.csv"),
        "dropout_report": str(RUNS_DIR / "dropout_ablation_summary.md") if (RUNS_DIR / "dropout_ablation_summary.md").exists() else None,
        "qualitative_manifest": read_csv(RUNS_DIR / "qualitative_cases_manifest.csv"),
        "qualitative_report": str(RUNS_DIR / "qualitative_cases_summary.md") if (RUNS_DIR / "qualitative_cases_summary.md").exists() else None,
        "phase3a_report": str(RUNS_DIR / "phase3a_report.md") if (RUNS_DIR / "phase3a_report.md").exists() else None,
    }


def collect_phase3b():
    return {
        "split_summary": read_csv(RUNS_DIR / "split_integrity_summary.csv"),
        "nearest_pair_count": count_csv_rows(RUNS_DIR / "split_integrity_nearest_pairs.csv"),
        "manual_review_count": count_csv_rows(RUNS_DIR / "split_integrity_manual_review.csv"),
        "exact_duplicate_count": count_csv_rows(RUNS_DIR / "split_integrity_exact_duplicates.csv"),
        "split_report": str(RUNS_DIR / "split_integrity_summary.md") if (RUNS_DIR / "split_integrity_summary.md").exists() else None,
        "selection_note": str(RUNS_DIR / "dropout_ratio_selection_note.md") if (RUNS_DIR / "dropout_ratio_selection_note.md").exists() else None,
        "phase3b_report": str(RUNS_DIR / "phase3b_report.md") if (RUNS_DIR / "phase3b_report.md").exists() else None,
    }


def collect_phase3c():
    return {
        "rgb_duplicate_summary": read_csv(RUNS_DIR / "rgb_cross_split_duplicate_summary.csv"),
        "rgb_exact_pair_count": count_csv_rows(RUNS_DIR / "rgb_cross_split_exact_pairs.csv"),
        "rgb_group_count": count_csv_rows(RUNS_DIR / "rgb_cross_split_group_stats.csv"),
        "blocked_split_summary": read_csv(RUNS_DIR / "blocked_split_proposal_summary.csv"),
        "strata_summary": read_csv(RUNS_DIR / "rgb_separation_strata_summary.csv"),
        "rgb_duplicate_report": str(RUNS_DIR / "rgb_cross_split_duplicate_summary.md")
        if (RUNS_DIR / "rgb_cross_split_duplicate_summary.md").exists()
        else None,
        "blocked_split_report": str(RUNS_DIR / "blocked_split_proposal_summary.md")
        if (RUNS_DIR / "blocked_split_proposal_summary.md").exists()
        else None,
        "strata_report": str(RUNS_DIR / "rgb_separation_strata_summary.md")
        if (RUNS_DIR / "rgb_separation_strata_summary.md").exists()
        else None,
        "phase3c_report": str(RUNS_DIR / "phase3c_report.md") if (RUNS_DIR / "phase3c_report.md").exists() else None,
    }


def collect_phase4a():
    return {
        "clean_protocol": str(RUNS_DIR / "clean_block64g16_protocol.md")
        if (RUNS_DIR / "clean_block64g16_protocol.md").exists()
        else None,
        "clean_summary": read_csv(RUNS_DIR / "clean_block64g16_summary.csv"),
        "clean_summary_report": str(RUNS_DIR / "clean_block64g16_summary.md")
        if (RUNS_DIR / "clean_block64g16_summary.md").exists()
        else None,
        "phase4a_report": str(RUNS_DIR / "phase4a_report.md") if (RUNS_DIR / "phase4a_report.md").exists() else None,
        "b0_eval": read_key_value_file(RUNS_DIR / "B0_early_block64g16_e50" / "eval_thr050" / "eval_results.txt"),
        "b1_eval": read_key_value_file(RUNS_DIR / "B1_reliability_p000_block64g16_e50" / "eval_thr050" / "eval_results.txt"),
        "b2_eval": read_key_value_file(RUNS_DIR / "B2_reliability_p015_block64g16_e50" / "eval_thr050" / "eval_results.txt"),
        "b4_eval": read_key_value_file(RUNS_DIR / "B4_reliability_p020_block64g16_e50" / "eval_thr050" / "eval_results.txt"),
        "b1_missing": read_csv(RUNS_DIR / "B1_reliability_p000_block64g16_e50" / "missing_modality" / "missing_modality_results.csv"),
        "b2_missing": read_csv(RUNS_DIR / "B2_reliability_p015_block64g16_e50" / "missing_modality" / "missing_modality_results.csv"),
        "b4_missing": read_csv(RUNS_DIR / "B4_reliability_p020_block64g16_e50" / "missing_modality" / "missing_modality_results.csv"),
    }


def collect_phase4b():
    return {
        "smoke_test": str(RUNS_DIR / "seed_reproducibility_smoke.md")
        if (RUNS_DIR / "seed_reproducibility_smoke.md").exists()
        else None,
        "seed_replication": read_csv(RUNS_DIR / "clean_block64g16_seed_replication.csv"),
        "seed_replication_report": str(RUNS_DIR / "clean_block64g16_seed_replication.md")
        if (RUNS_DIR / "clean_block64g16_seed_replication.md").exists()
        else None,
        "phase4b_report": str(RUNS_DIR / "phase4b_report.md") if (RUNS_DIR / "phase4b_report.md").exists() else None,
        "decision": read_last_nonempty_line(RUNS_DIR / "phase4b_report.md"),
        "r1_missing_seed0": read_csv(
            RUNS_DIR / "R1_reliability_p000_seed0_block64g16_e50" / "missing_modality" / "missing_modality_results.csv"
        ),
        "r1_missing_seed2": read_csv(
            RUNS_DIR / "R1_reliability_p000_seed2_block64g16_e50" / "missing_modality" / "missing_modality_results.csv"
        ),
        "r2_missing_seed0": read_csv(
            RUNS_DIR / "R2_reliability_p015_seed0_block64g16_e50" / "missing_modality" / "missing_modality_results.csv"
        ),
        "r2_missing_seed2": read_csv(
            RUNS_DIR / "R2_reliability_p015_seed2_block64g16_e50" / "missing_modality" / "missing_modality_results.csv"
        ),
        "r4_missing_seed0": read_csv(
            RUNS_DIR / "R4_reliability_p020_seed0_block64g16_e50" / "missing_modality" / "missing_modality_results.csv"
        ),
        "r4_missing_seed2": read_csv(
            RUNS_DIR / "R4_reliability_p020_seed2_block64g16_e50" / "missing_modality" / "missing_modality_results.csv"
        ),
    }


def read_last_nonempty_line(path):
    if not path.exists():
        return None
    for line in reversed(path.read_text(encoding="utf-8").splitlines()):
        stripped = line.strip()
        if stripped:
            return stripped
    return None


def best_by(results, metric):
    numeric = []
    for row in results:
        try:
            numeric.append((float(row.get(metric) or "nan"), row))
        except ValueError:
            continue
    if not numeric:
        return None
    return max(numeric, key=lambda item: item[0])[1]


def build_handoff():
    eval_results = collect_eval_results()
    best_ap50 = best_by(eval_results, "ap50")
    best_ap75 = best_by(eval_results, "ap75")
    status_short = git_lines(["status", "--short"])
    branch = git_lines(["branch", "--show-current"])
    remotes = git_lines(["remote", "-v"])

    return {
        "project_name": "RA-RepDet-TriAir",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "workspace": str(PROJECT_ROOT),
        "git": {
            "branch": branch[0] if branch else None,
            "remotes": remotes,
            "status_short": status_short,
        },
        "dataset": {
            "root": r"D:\download\triair",
            "samples": 10489,
            "images_with_label_txt": 9751,
            "images_without_label_txt": 738,
            "empty_label_txt_files": 1,
            "classes": 1,
            "total_valid_boxes": 30634,
            "val_images": 2098,
            "val_boxes": 6074,
            "note": "Missing txt files are treated as empty-target images.",
        },
        "models": {
            "E0": "5-channel early fusion -> 1x1 Conv(5,3) -> RepViT-M0.9 -> FPN -> FCOS.",
            "E1": "RGB/Thermal/Event reliability stems -> alpha fusion -> Conv(16,3) -> RepViT-M0.9 -> FPN -> FCOS.",
            "E2": "E1 plus modality dropout 0.15 during training.",
            "E3": "E1 plus modality dropout 0.10 during training.",
            "E4": "E1 plus modality dropout 0.20 during training.",
            "E5": "Availability-conditioned reliability fusion with post-stem masking, masked softmax, and modality dropout 0.15.",
            "E6": "E2 inference architecture trained with modality-subset consistency distillation from frozen E2 full-input teacher.",
            "labels": "TriAir class 0 is shifted to torchvision detection label 1; background remains 0.",
        },
        "core_results": eval_results,
        "best_model": {
            "by_ap50": best_ap50,
            "by_ap75": best_ap75,
        },
        "missing_modality": collect_missing_modality(),
        "profile": collect_profile(),
        "phase2a": collect_phase2a(),
        "phase2b": collect_phase2b(),
        "phase2c": collect_phase2c(),
        "phase3a": collect_phase3a(),
        "phase3b": collect_phase3b(),
        "phase3c": collect_phase3c(),
        "phase4a": collect_phase4a(),
        "phase4b": collect_phase4b(),
        "current_pending_experiments": [
            "Use runs/phase4b_report.md as the controlled-seed clean-split decision gate once Phase 4B completes.",
            "Former random-split results are historical diagnostics only and must not be paper headline results.",
            "Do not start 100-epoch training until the Phase 4B decision gate is reviewed.",
        ],
        "code_structure": {
            "dataset": "datasets/triair_dataset.py",
            "split_tool": "tools/create_triair_split.py",
            "training": "rarepdet/train_early_fusion.py",
            "evaluation": "rarepdet/eval_map.py",
            "visualization": "rarepdet/val_early_fusion.py",
            "backbones": "rarepdet/models/repvit_fpn_backbone.py",
            "detector_builder": "rarepdet/models/early_fusion_fcos.py",
            "postprocessing_tools": "rarepdet/tools/",
        },
        "recent_modified_files": status_short,
        "next_recommended_tasks": [
            "Use E2 as the main robustness model unless the paper specifically needs the alpha-correctness ACRF ablation.",
            "Use E5 as an ablation showing exact zero absent-modality alpha with a small parameter increase.",
            "Use E6 as a training-strategy ablation because Phase 2C did not satisfy the E2 replacement rule.",
            "Use E2 for accuracy-first reporting and E4 as a robustness-first variant unless later split/seed audits change the decision.",
            "Use the Phase 4B R-run table for clean-split headline model selection.",
        ],
    }


def write_markdown(data, path):
    lines = [
        "# RA-RepDet-TriAir Handoff",
        "",
        f"Generated: {data['generated_at']}",
        f"Workspace: `{data['workspace']}`",
        "",
        "## Dataset",
        "",
        f"- Root: `{data['dataset']['root']}`",
        f"- Samples: {data['dataset']['samples']}",
        f"- Images with label txt: {data['dataset']['images_with_label_txt']}",
        f"- Images without label txt: {data['dataset']['images_without_label_txt']}",
        f"- Empty label txt files: {data['dataset']['empty_label_txt_files']}",
        f"- Total valid boxes: {data['dataset']['total_valid_boxes']}",
        f"- Val images / boxes: {data['dataset']['val_images']} / {data['dataset']['val_boxes']}",
        f"- Note: {data['dataset']['note']}",
        "",
        "## Core Results",
        "",
        "| Method | Precision | Recall | AP50 | AP75 | GT boxes | Predictions | Mean Confidence |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in data["core_results"]:
        lines.append(
            "| {id} {method} | {precision} | {recall} | {ap50} | {ap75} | {gt_boxes} | {predictions} | {mean_confidence} |".format(
                **{key: row.get(key) or "" for key in row}
            )
        )

    best_ap50 = data["best_model"]["by_ap50"] or {}
    best_ap75 = data["best_model"]["by_ap75"] or {}
    lines += [
        "",
        "## Best Model",
        "",
        f"- Best AP50: {best_ap50.get('id', 'NA')} {best_ap50.get('method', '')} ({best_ap50.get('ap50', 'NA')})",
        f"- Best AP75: {best_ap75.get('id', 'NA')} {best_ap75.get('method', '')} ({best_ap75.get('ap75', 'NA')})",
        "",
        "## Phase 2A Outputs",
        "",
        "- Report: `runs/phase2a_report.md`" if data["phase2a"]["report"] else "- Report: NA",
        f"- Main table rows: {len(data['phase2a']['main_results'])}",
        f"- E0 profile rows: {len(data['phase2a']['profile_e0'])}",
        f"- E2 profile rows: {len(data['phase2a']['profile_e2'])}",
        f"- Brightness-proxy rows: {len(data['phase2a']['brightness_proxy'])}",
        f"- Alpha mode rows: {len(data['phase2a']['alpha_modes'])}",
        "",
        "## Phase 2B ACRF Outputs",
        "",
        "- Report: `runs/acrf_evidence_report.md`" if data["phase2b"]["evidence_report"] else "- Report: NA",
        "- Smoke test: `runs/acrf_smoke_test.md`" if data["phase2b"]["smoke_test"] else "- Smoke test: NA",
        f"- Evidence rows: {len(data['phase2b']['evidence_summary'])}",
        f"- E5 missing-modality rows: {len(data['phase2b']['e5_missing_modality'])}",
        f"- E5 alpha-mode rows: {len(data['phase2b']['e5_alpha_modes'])}",
        "",
        "## Phase 2C MSCD Outputs",
        "",
        "- Report: `runs/mscd_evidence_report.md`" if data["phase2c"]["evidence_report"] else "- Report: NA",
        "- Phase 2C report: `runs/phase2c_report.md`" if data["phase2c"]["phase2c_report"] else "- Phase 2C report: NA",
        "- Smoke test: `runs/mscd_smoke_test.md`" if data["phase2c"]["smoke_test"] else "- Smoke test: NA",
        f"- Evidence rows: {len(data['phase2c']['evidence_summary'])}",
        f"- E6 missing-modality rows: {len(data['phase2c']['e6_missing_modality'])}",
        "",
        "## Phase 3A Outputs",
        "",
        "- Dropout report: `runs/dropout_ablation_summary.md`" if data["phase3a"]["dropout_report"] else "- Dropout report: NA",
        "- Qualitative report: `runs/qualitative_cases_summary.md`" if data["phase3a"]["qualitative_report"] else "- Qualitative report: NA",
        "- Phase 3A report: `runs/phase3a_report.md`" if data["phase3a"]["phase3a_report"] else "- Phase 3A report: NA",
        f"- Dropout ablation rows: {len(data['phase3a']['dropout_ablation'])}",
        f"- Qualitative manifest rows: {len(data['phase3a']['qualitative_manifest'])}",
        "",
        "## Phase 3B Outputs",
        "",
        "- Split-integrity report: `runs/split_integrity_summary.md`" if data["phase3b"]["split_report"] else "- Split-integrity report: NA",
        "- Dropout selection note: `runs/dropout_ratio_selection_note.md`" if data["phase3b"]["selection_note"] else "- Dropout selection note: NA",
        "- Phase 3B report: `runs/phase3b_report.md`" if data["phase3b"]["phase3b_report"] else "- Phase 3B report: NA",
        f"- Split summary rows: {len(data['phase3b']['split_summary'])}",
        f"- Nearest-pair rows: {data['phase3b']['nearest_pair_count']}",
        f"- Manual-review rows: {data['phase3b']['manual_review_count']}",
        f"- Exact duplicate rows: {data['phase3b']['exact_duplicate_count']}",
        "",
        "## Phase 3C Outputs",
        "",
        "- RGB duplicate report: `runs/rgb_cross_split_duplicate_summary.md`" if data["phase3c"]["rgb_duplicate_report"] else "- RGB duplicate report: NA",
        "- Blocked split report: `runs/blocked_split_proposal_summary.md`" if data["phase3c"]["blocked_split_report"] else "- Blocked split report: NA",
        "- RGB strata report: `runs/rgb_separation_strata_summary.md`" if data["phase3c"]["strata_report"] else "- RGB strata report: NA",
        "- Phase 3C report: `runs/phase3c_report.md`" if data["phase3c"]["phase3c_report"] else "- Phase 3C report: NA",
        f"- RGB duplicate summary rows: {len(data['phase3c']['rgb_duplicate_summary'])}",
        f"- RGB exact pair rows: {data['phase3c']['rgb_exact_pair_count']}",
        f"- RGB group rows: {data['phase3c']['rgb_group_count']}",
        f"- Blocked split candidate rows: {len(data['phase3c']['blocked_split_summary'])}",
        f"- RGB strata rows: {len(data['phase3c']['strata_summary'])}",
        "",
        "## Phase 4A Outputs",
        "",
        "- Clean split protocol: `runs/clean_block64g16_protocol.md`" if data["phase4a"]["clean_protocol"] else "- Clean split protocol: NA",
        "- Clean summary: `runs/clean_block64g16_summary.md`" if data["phase4a"]["clean_summary_report"] else "- Clean summary: NA",
        "- Phase 4A report: `runs/phase4a_report.md`" if data["phase4a"]["phase4a_report"] else "- Phase 4A report: NA",
        f"- Clean summary rows: {len(data['phase4a']['clean_summary'])}",
        f"- B1 missing-modality rows: {len(data['phase4a']['b1_missing'])}",
        f"- B2 missing-modality rows: {len(data['phase4a']['b2_missing'])}",
        f"- B4 missing-modality rows: {len(data['phase4a']['b4_missing'])}",
        "",
        "## Phase 4B Controlled-Seed Outputs",
        "",
        "- Smoke test: `runs/seed_reproducibility_smoke.md`" if data["phase4b"]["smoke_test"] else "- Smoke test: NA",
        "- Seed replication report: `runs/clean_block64g16_seed_replication.md`"
        if data["phase4b"]["seed_replication_report"]
        else "- Seed replication report: NA",
        "- Phase 4B report: `runs/phase4b_report.md`" if data["phase4b"]["phase4b_report"] else "- Phase 4B report: NA",
        f"- Seed replication rows: {len(data['phase4b']['seed_replication'])}",
        f"- R1 missing-modality rows: {len(data['phase4b']['r1_missing_seed0']) + len(data['phase4b']['r1_missing_seed2'])}",
        f"- R2 missing-modality rows: {len(data['phase4b']['r2_missing_seed0']) + len(data['phase4b']['r2_missing_seed2'])}",
        f"- R4 missing-modality rows: {len(data['phase4b']['r4_missing_seed0']) + len(data['phase4b']['r4_missing_seed2'])}",
        f"- Decision: {data['phase4b']['decision'] or 'NA'}",
        "",
        "## Model And Code Structure",
        "",
    ]
    for key, value in data["models"].items():
        lines.append(f"- {key}: {value}")
    lines.append("")
    for key, value in data["code_structure"].items():
        lines.append(f"- {key}: `{value}`")

    lines += [
        "",
        "## Current Pending Experiments",
        "",
    ]
    lines += [f"- {item}" for item in data["current_pending_experiments"]]

    lines += [
        "",
        "## Recently Modified Files",
        "",
    ]
    if data["recent_modified_files"]:
        lines += [f"- `{item}`" for item in data["recent_modified_files"]]
    else:
        lines.append("- Working tree was clean when this report was generated.")

    lines += [
        "",
        "## Next Recommended Tasks",
        "",
    ]
    lines += [f"- {item}" for item in data["next_recommended_tasks"]]
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main():
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    data = build_handoff()
    json_path = RUNS_DIR / "handoff_latest.json"
    md_path = RUNS_DIR / "handoff_latest.md"
    json_path.write_text(json.dumps(data, indent=2, ensure_ascii=True), encoding="utf-8")
    write_markdown(data, md_path)
    print(f"Saved: {md_path}")
    print(f"Saved: {json_path}")


if __name__ == "__main__":
    main()
