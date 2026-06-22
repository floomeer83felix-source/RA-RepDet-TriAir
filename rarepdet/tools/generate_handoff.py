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
        "current_pending_experiments": [
            "Review Phase 3A dropout ablation in runs/dropout_ablation_summary.md.",
            "Use runs/qualitative_cases_manifest.csv to assemble paper figure panels outside Git.",
            "Keep the selected default dropout ratio documented in runs/phase3a_report.md.",
            "Prepare manuscript tables from Phase 2A, Phase 2B, Phase 2C, and Phase 3A summaries.",
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
            "Use the Phase 3A dropout-ratio report to justify the final default dropout value.",
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
