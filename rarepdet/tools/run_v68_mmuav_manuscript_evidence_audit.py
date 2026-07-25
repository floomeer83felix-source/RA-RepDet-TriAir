"""Build the CPU-only V68 MM-UAV manuscript-evidence audit package."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import statistics
import subprocess
from decimal import Decimal, getcontext
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "runs/v68_mmuav_manuscript_evidence_audit"
START_COMMIT = "c40d51f96ee56094f22b879d1fe88f385d177325"
V67_COMMIT = "305a49f06483923eadf7c2a60048a2ca51e7743c"
DECISION = "V68_BLOCKED_DATA_RIGHTS_OR_CITATION_INCOMPLETE"
METRICS = ("ap50_95", "ap50", "ap75", "ar1", "ar10", "ar100")
LABELS = {
    "ap50_95": "AP",
    "ap50": "AP50",
    "ap75": "AP75",
    "ar1": "AR@1",
    "ar10": "AR@10",
    "ar100": "AR@100",
}
EVIDENCE = {
    "v65_final": (
        "runs/v65_mmuav_seed0_softplus_fulltrain_feasibility/final_decision.json",
        "977c35622147d72c08edc86ffbdd34cf05ab6ec0ab5fb0548acd9087d3d1bf9e",
    ),
    "v65_safety": (
        "runs/v65_mmuav_seed0_softplus_fulltrain_feasibility/safety_audit.json",
        "27b8534aaf3746a721d12b05d89e7f3d7573d244b935d01903d5a6355d5a00f2",
    ),
    "v65_metrics": (
        "runs/v65_mmuav_seed0_softplus_fulltrain_feasibility/full_devval_metrics.json",
        "e6e5bde9db36c01ef052ac11339116d73916ee1a04749099ec9e077b1c9604ac",
    ),
    "v66_final": (
        "runs/v66_mmuav_seed1_softplus_fulltrain_confirmation/final_decision.json",
        "08bca25ba87de913a8f2088de73b3df8443a177aa24ecb1dee017486e3cb4709",
    ),
    "v66_safety": (
        "runs/v66_mmuav_seed1_softplus_fulltrain_confirmation/safety_audit.json",
        "441a0e4d641f1fc8adda5ee453dc95553943cac240fcb48444a5327cd2e57687",
    ),
    "v66_metrics": (
        "runs/v66_mmuav_seed1_softplus_fulltrain_confirmation/full_devval_metrics.json",
        "2a8510e2cdce7e65441fff5f5344d1de984e02ffd1ca5fc57f6bc4962511eb89",
    ),
    "v67_final": (
        "runs/v67_mmuav_two_seed_reliability_softplus_benchmark/final_decision.json",
        "171b059821a06272793b2a037b8dad7c18de97bf06f45f396fbad08f5ad4e1f4",
    ),
    "v67_safety": (
        "runs/v67_mmuav_two_seed_reliability_softplus_benchmark/safety_audit.json",
        "257eb16bbb3aaaca702a10c516933de0af961efedf7f281b32df400b1d1ac862",
    ),
    "v67_comparison": (
        "runs/v67_mmuav_two_seed_reliability_softplus_benchmark/matched_comparison_summary.json",
        "98165ed7aa4468cd83ab2008cd379434121d09cd81670698e9795ef392eafe63",
    ),
    "v67_seed0_metrics": (
        "runs/v67_mmuav_two_seed_reliability_softplus_benchmark/seed0_full_devval_metrics.json",
        "f4b80c73025b8f8592152e17df67867e932146d85b4bc87547538c17de307805",
    ),
    "v67_seed1_metrics": (
        "runs/v67_mmuav_two_seed_reliability_softplus_benchmark/seed1_full_devval_metrics.json",
        "44f3782e367be88857ceeb5ed6e5c6491c23a3c020360d05c9f6a125efd21b27",
    ),
}
RIGHTS_SOURCES = {
    "license_contract": (
        "runs/v52_mmuav_audit/license_contract.json",
        "c9f8e86a9795238ffcc39e94a56ba6a9a7350087cdf493c1b0ce9c0cc6d4408e",
    ),
    "provider_contract": (
        "runs/v52_mmuav_audit/provider_contract_audit.json",
        "e69609fabe6dcdc6329476cb2b981c1387ba1106dbeb0503f3dbfe7bb25b1866",
    ),
    "provenance": (
        "runs/v52_mmuav_audit/provenance_and_license.md",
        "9cc6fb0c8c382accad05cc2499ad11a1645cab24d03be2ca7ba8a8f6e7564a44",
    ),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def write_json(name: str, payload: object) -> None:
    (OUT / name).write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def protected_paths() -> list[Path]:
    selected: list[Path] = []
    historical = re.compile(r"^runs/v(?:4[0-9]|5[0-9]|6[0-7])_")
    fixed = {
        "rarepdet/train_early_fusion.py",
        "rarepdet/models/early_fusion_fcos.py",
        "rarepdet/models/reliability_fusion_fcos.py",
        "datasets/triair_dataset.py",
        "main.tex",
        "main_sivp_snjnl.tex",
    }
    for relative in git("ls-files").splitlines():
        if (
            relative in fixed
            or historical.match(relative)
            or relative.startswith("manuscript/")
            or relative.startswith("submission/")
        ):
            path = ROOT / relative
            if path.is_file():
                selected.append(path)
    return sorted(selected)


def protected_fingerprint() -> dict[str, object]:
    records = [
        {"path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path), "bytes": path.stat().st_size}
        for path in protected_paths()
    ]
    encoded = json.dumps(records, sort_keys=True, separators=(",", ":")).encode()
    return {
        "file_count": len(records),
        "aggregate_sha256": hashlib.sha256(encoded).hexdigest(),
        "files": records,
    }


def verify_evidence() -> dict[str, object]:
    records: dict[str, object] = {}
    for key, (relative, expected) in {**EVIDENCE, **RIGHTS_SOURCES}.items():
        actual = sha256(ROOT / relative)
        records[key] = {
            "path": relative,
            "expected_sha256": expected,
            "actual_sha256": actual,
            "match": actual == expected,
        }
    v65_final = read_json(EVIDENCE["v65_final"][0])
    v66_final = read_json(EVIDENCE["v66_final"][0])
    v67_final = read_json(EVIDENCE["v67_final"][0])
    v65_safety = read_json(EVIDENCE["v65_safety"][0])
    v66_safety = read_json(EVIDENCE["v66_safety"][0])
    v67_safety = read_json(EVIDENCE["v67_safety"][0])
    decisions = {
        "v65": v65_final["decision"] == "V65_FULLTRAIN_COMPLETE_NONZERO_AP",
        "v66": v66_final["decision"] == "V66_SEED1_FULLTRAIN_COMPLETE_NONZERO_AP",
        "v67": v67_final["decision"] == "V67_TWO_SEED_RELIABILITY_FULLTRAIN_COMPLETE",
    }
    safety = {
        "v65_steps": v65_safety["optimizer_steps"] == 7187,
        "v65_evaluation": v65_safety["evaluation_attempts"] == 1 and v65_safety["full_devval_rows"] == 1845,
        "v66_steps": v66_safety["optimizer_steps"] == 7187,
        "v66_evaluation": v66_safety["evaluation_attempts"] == 1 and v66_safety["full_devval_rows"] == 1845,
        "v67_steps": v67_safety["optimizer_steps"] == 14374,
        "v67_probes": v67_safety["probe_backward_calls"] == 80,
        "v67_snapshots": v67_safety["verified_recovery_snapshots"] == 38,
        "v67_evaluations": v67_safety["evaluation_attempts_per_seed"] == 1,
        "v67_finite": v67_safety["all_finite"],
    }
    checks = {
        "all_hashes_match": all(record["match"] for record in records.values()),
        "all_decisions_match": all(decisions.values()),
        "all_safety_contracts_match": all(safety.values()),
        "v67_commit_is_ancestor": subprocess.run(
            ["git", "merge-base", "--is-ancestor", V67_COMMIT, "HEAD"], cwd=ROOT
        ).returncode
        == 0,
    }
    if not all(checks.values()):
        raise RuntimeError(f"V68 frozen-evidence mismatch: {checks}")
    return {"starting_commit": START_COMMIT, "records": records, "decisions": decisions, "safety": safety, "checks": checks}


def source_metrics() -> dict[str, dict[int, dict[str, float]]]:
    return {
        "equal": {
            0: {key: read_json(EVIDENCE["v65_metrics"][0])[key] for key in METRICS},
            1: {key: read_json(EVIDENCE["v66_metrics"][0])[key] for key in METRICS},
        },
        "reliability": {
            0: {key: read_json(EVIDENCE["v67_seed0_metrics"][0])[key] for key in METRICS},
            1: {key: read_json(EVIDENCE["v67_seed1_metrics"][0])[key] for key in METRICS},
        },
    }


def calculate_table() -> tuple[list[dict[str, str]], dict[str, object]]:
    values = source_metrics()
    comparison = read_json(EVIDENCE["v67_comparison"][0])
    rows: list[dict[str, str]] = []
    numeric: dict[str, object] = {"methods": {}, "deltas": {}}
    for method in ("equal", "reliability"):
        numeric["methods"][method] = {}
        for seed in (0, 1):
            rows.append(
                {"row_type": "seed", "method": method, "seed": str(seed)}
                | {LABELS[key]: f"{values[method][seed][key]:.10f}" for key in METRICS}
            )
        for summary_name in ("mean", "sample_std"):
            summary_values: dict[str, float] = {}
            row = {"row_type": summary_name, "method": method, "seed": "both"}
            for key in METRICS:
                pair = [values[method][seed][key] for seed in (0, 1)]
                result = statistics.mean(pair) if summary_name == "mean" else statistics.stdev(pair)
                summary_values[key] = result
                row[LABELS[key]] = f"{result:.10f}"
            numeric["methods"][method][summary_name] = summary_values
            rows.append(row)
    for seed in (0, 1):
        delta_values = {key: values["reliability"][seed][key] - values["equal"][seed][key] for key in METRICS}
        numeric["deltas"][str(seed)] = delta_values
        rows.append(
            {"row_type": "matched_delta", "method": "reliability-minus-equal", "seed": str(seed)}
            | {LABELS[key]: f"{delta_values[key]:+.10f}" for key in METRICS}
        )
    mean_delta = {
        key: statistics.mean([numeric["deltas"][str(seed)][key] for seed in (0, 1)]) for key in METRICS
    }
    numeric["deltas"]["mean"] = mean_delta
    rows.append(
        {"row_type": "mean_matched_delta", "method": "reliability-minus-equal", "seed": "both"}
        | {LABELS[key]: f"{mean_delta[key]:+.10f}" for key in METRICS}
    )

    getcontext().prec = 40
    independent: dict[str, object] = {}
    for method in ("equal", "reliability"):
        independent[method] = {}
        for key in METRICS:
            a, b = (Decimal(str(values[method][seed][key])) for seed in (0, 1))
            mean = (a + b) / Decimal(2)
            sample_std = (((a - mean) ** 2 + (b - mean) ** 2) / Decimal(1)).sqrt()
            independent[method][key] = {"mean": str(mean), "sample_std": str(sample_std)}
            if abs(float(mean) - numeric["methods"][method]["mean"][key]) > 1e-15:
                raise RuntimeError(f"V68 mean arithmetic mismatch: {method} {key}")
            if abs(float(sample_std) - numeric["methods"][method]["sample_std"][key]) > 1e-15:
                raise RuntimeError(f"V68 standard-deviation arithmetic mismatch: {method} {key}")
    for seed in (0, 1):
        for key in METRICS:
            frozen = comparison["per_seed"][str(seed)][key]["reliability_minus_equal"]
            if abs(frozen - numeric["deltas"][str(seed)][key]) > 1e-15:
                raise RuntimeError(f"V68 matched-delta mismatch: seed={seed} {key}")
    return rows, {
        "numeric": numeric,
        "independent_decimal_path": independent,
        "frozen_v67_comparison_matched": True,
        "rounding_policy": "All paper tables use fixed 10 decimal places; calculations use unrounded source values.",
    }


def write_table(rows: list[dict[str, str]]) -> None:
    fields = ["row_type", "method", "seed", *[LABELS[key] for key in METRICS]]
    with (OUT / "matched_metrics_table.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    lines = [
        "# V68 Matched MM-UAV Metrics",
        "",
        "| Row | Method | Seed | AP | AP50 | AP75 | AR@1 | AR@10 | AR@100 |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['row_type']} | {row['method']} | {row['seed']} | "
            + " | ".join(row[LABELS[key]] for key in METRICS)
            + " |"
        )
    lines.extend(
        [
            "",
            "Values are reproduced from immutable V65-V67 final-metric files. Means and sample standard deviations use the two frozen seeds. Deltas are reliability minus equal fusion at the matched seed.",
        ]
    )
    (OUT / "matched_metrics_table.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_narrative_outputs() -> None:
    (OUT / "protocol.md").write_text(
        """# V68 MM-UAV Manuscript-Evidence Audit Protocol

- CPU/documentation only; CUDA, training, evaluation, tuning, and selection are prohibited.
- Starting commit: `c40d51f96ee56094f22b879d1fe88f385d177325`.
- V65-V67 metrics are read from immutable final evidence and checked against frozen SHA256 values.
- Means and sample standard deviations are reproduced with Python `statistics` and an independent high-precision Decimal path.
- Historical evidence, production code, active manuscript sources, and submission files are fingerprinted before and after generation.
- Dataset rights are assessed only from preserved provider-controlled or repository audit records. Local possession is not treated as permission.
""",
        encoding="utf-8",
    )
    (OUT / "protocol_difference_matrix.md").write_text(
        """# MM-UAV Versus TriAir Protocol Difference Matrix

| Dimension | MM-UAV V65-V67 | Current TriAir headline protocol | Manuscript consequence |
|---|---|---|---|
| Role | Matched two-seed devval stress test | Primary within-TriAir headline evaluation | MM-UAV is not an external replication of the headline configuration |
| Input size | 320 x 320 | 640 x 640 | Resolution and compute regime differ |
| Training length | One ordered pass, 7,187 optimizer steps | 50 epochs | Optimization exposure is not matched |
| Modal path | Independent RGB/IR/event stems with learned IR/event feature alignment to RGB | Modality-specific stems and sample-dependent fusion on the TriAir five-channel representation | Alignment and input contracts differ |
| Fusion comparison | Equal weights versus active shared V57 reliability scorer | Early fusion, dynamic reliability fusion, controls, and preselected dropout configuration | The intervention families are not identical |
| Bbox activation | Softplus(beta=1, threshold=20) distance head | Current production/headline detector path; no V65-V67 Softplus intervention | Head behavior differs |
| Modality dropout | None | Headline configuration uses preselected p=0.15 | V67 does not replicate the full headline method |
| Split/evaluation | Frozen source-train-derived train/devval; devval is not an independent test set | Component-disjoint development-validation plus locked within-dataset holdout | Neither protocol supplies cross-dataset independent-test evidence |
| Seeds | Two matched initialization states | Three paired seeds in the current active manuscript | Replication depth differs |
| Claims | Descriptive stress-test evidence only | Descriptive within-TriAir evidence only | No external-generalization bridge is permitted |

TriAir protocol facts are sourced from `main.tex` and `manuscript/tables/Table_2_implementation_and_reproducibility.csv`; MM-UAV facts are sourced from V53 and V65-V67 protocol/configuration records.
""",
        encoding="utf-8",
    )
    (OUT / "claim_matrix.md").write_text(
        """# V68 Claim Matrix

| Proposed statement | Status | Required wording or reason |
|---|---|---|
| V65-V67 form a matched two-seed MM-UAV devval stress test | Allowed with qualification | Name devval, two seeds, frozen one-pass protocol, and no independent test |
| Both methods completed the frozen protocol with finite nonzero AP | Allowed | Trace to V65-V67 safety and final metrics |
| The scorer learned non-uniform weights | Allowed with qualification | Describe softmax model outputs, not calibrated physical reliability |
| Paired AP increased for seed 0 and decreased for seed 1 | Allowed | Report both directions and exact deltas |
| Mean paired AP delta was +0.0018592721 | Allowed with qualification | State descriptive n=2 result and large seed spread |
| Reliability fusion consistently improves MM-UAV | Disallowed | Paired direction is mixed |
| Reliability fusion significantly improves MM-UAV | Disallowed | No inferential test and n=2 |
| V67 proves external generalization of the TriAir headline model | Disallowed | Dataset and protocol differ; MM-UAV is not the headline configuration |
| Fusion weights measure sensor health or calibrated reliability | Disallowed | They are learned model coefficients without calibration evidence |
| MM-UAV devval is an independent test set | Disallowed | It is source-train-derived devval |
| Results support broad robustness or deployment | Disallowed | No real sensor-failure, independent-test, or deployment study |
| MM-UAV aggregate metrics may appear in the submission | Qualification required and currently blocked | Provider identity, dataset citation, dataset license, research-use grant, and reporting permission must be documented first |
""",
        encoding="utf-8",
    )
    (OUT / "data_rights_and_citation_audit.md").write_text(
        """# V68 MM-UAV Data Rights And Citation Audit

## Available source-backed facts

- Dataset name used in the records: `MM-UAV`; extracted internal directory label: `MMMUAV`.
- An official benchmark repository and evaluation repository were audited at pinned commits, and an arXiv v3 record (`2511.18344v3`) was preserved by URL and SHA256 in V52.
- The repository code license is Apache-2.0. V52 explicitly records that this covers repository code and is not an express license for dataset files.
- The arXiv content license recorded by V52 is not a dataset-use grant.
- No dataset README, provider metadata, version identifier, or dataset license text was present in the extracted subset or preserved archive inventory.
- V52 found no explicit dataset research-use grant, reporting permission, or redistribution permission.

## Required rights fields

| Field | Status | Evidence and consequence |
|---|---|---|
| Canonical dataset name | Partial | `MM-UAV` is used consistently, but a provider-issued data card/version record is absent |
| Provider / release authority | Unresolved | Official code sources exist, but the dataset release authority is not established in preserved records |
| Submission-ready citation | Incomplete | An arXiv record is identified, but canonical dataset citation metadata is not preserved as a verified repository citation |
| Dataset version | Unresolved | No version identifier was found |
| Dataset license | Unresolved | Code and paper licenses do not grant dataset rights |
| Research-use permission | Unresolved | Local possession and successful experimentation are not permission evidence |
| Aggregate-results reporting permission | Unresolved | No explicit term authorizes publication of derived benchmark metrics or methodological descriptions |
| Redistribution | Prohibited pending proof | No media, annotations, labels, transformed copies, or derivative data may be redistributed |

## Legal and ethical gate

The scientific evidence is internally auditable, but the available records do not establish that aggregate metrics and MM-UAV methodological descriptions may be included in a journal submission. V68 therefore fails closed. The blocker can be cleared only by provider-verifiable citation, dataset version, license/access terms, research-use permission, and permission to report aggregate derived results. No inference from code licensing, paper licensing, archive possession, or prior local use is acceptable.
""",
        encoding="utf-8",
    )
    (OUT / "manuscript_inclusion_recommendation.md").write_text(
        """# V68 Manuscript Inclusion Recommendation

## Recommendation

Exclude MM-UAV evidence from the current manuscript and keep V65-V67 internal until the data-rights and citation record is complete.

## Rationale

The metrics are reproducible and the matched design is useful as an internal stress test, but the paired AP direction is mixed and initialization sensitivity is large. The protocol also differs materially from the current TriAir headline configuration: 320 x 320 rather than 640 x 640, one ordered pass rather than 50 epochs, learned feature alignment, a Softplus bbox-distance path, no modality dropout, and source-train-derived devval rather than an external independent test.

More importantly, the provider, canonical citation, dataset version, dataset license, research-use grant, and aggregate-results reporting permission remain unresolved. That is a hard submission blocker independent of scientific strength. No appendix draft is created under the V68 contract.

## Reconsideration checklist

1. Obtain provider-verifiable canonical citation and dataset version.
2. Preserve the dataset license or access terms.
3. Confirm research use and publication of aggregate derived metrics are permitted.
4. Record redistribution restrictions explicitly.
5. Re-run this documentary gate without changing V65-V67 results.
""",
        encoding="utf-8",
    )


def run() -> None:
    if git("rev-parse", "HEAD") != START_COMMIT:
        raise RuntimeError(f"Unexpected V68 starting commit: {git('rev-parse', 'HEAD')}")
    if OUT.exists():
        raise RuntimeError(f"Refusing to overwrite existing V68 output: {OUT}")
    OUT.mkdir(parents=True)
    baseline = protected_fingerprint()
    evidence = verify_evidence()
    rows, arithmetic = calculate_table()
    write_table(rows)
    write_narrative_outputs()
    comparison = read_json(EVIDENCE["v67_comparison"][0])
    fusion = {
        "interpretation_boundary": "Learned softmax coefficients; not calibrated sensor-health measurements.",
        "seed0": comparison["fusion_diagnostics"]["0"],
        "seed1": comparison["fusion_diagnostics"]["1"],
        "checks": {
            "both_departed_from_uniform": all(
                comparison["fusion_diagnostics"][str(seed)]["departed_from_exact_uniform"] for seed in (0, 1)
            ),
            "both_finite": all(comparison["fusion_diagnostics"][str(seed)]["finite"] for seed in (0, 1)),
            "rgb_dominant_all_devval": all(
                comparison["fusion_diagnostics"][str(seed)]["dominant_modality_counts"]
                == {"rgb": 1845, "ir": 0, "event": 0}
                for seed in (0, 1)
            ),
        },
    }
    license_record = read_json(RIGHTS_SOURCES["license_contract"][0])
    rights = {
        "dataset_name": "MM-UAV",
        "provider": "unresolved",
        "canonical_citation": "incomplete",
        "dataset_version": "unresolved",
        "dataset_license": license_record["dataset_license"],
        "research_use_permission": "unresolved",
        "aggregate_reporting_permission": "unresolved",
        "redistribution_permission": "unresolved; fail-closed prohibition applies",
        "code_license_is_not_dataset_license": True,
        "paper_license_is_not_dataset_license": True,
        "submission_gate_passed": False,
    }
    manifest_sources = {
        key: {"path": relative, "sha256": sha256(ROOT / relative), "role": "frozen evidence"}
        for key, (relative, _) in {**EVIDENCE, **RIGHTS_SOURCES}.items()
    }
    for relative, role in (
        ("main.tex", "protected active manuscript protocol"),
        ("main_sivp_snjnl.tex", "protected active manuscript mirror"),
        ("manuscript/tables/Table_2_implementation_and_reproducibility.csv", "TriAir protocol source"),
        ("rarepdet/tools/run_v68_mmuav_manuscript_evidence_audit.py", "V68 generator"),
        ("tests/test_v68_mmuav_manuscript_evidence_audit.py", "V68 validation"),
    ):
        manifest_sources[relative] = {"path": relative, "sha256": sha256(ROOT / relative), "role": role}
    write_json("source_evidence_manifest.json", {"starting_commit": START_COMMIT, "sources": manifest_sources})
    write_json("v65_v66_v67_hash_verification.json", evidence)
    write_json("arithmetic_verification.json", arithmetic)
    write_json("fusion_weight_summary.json", fusion)
    write_json("data_rights_status.json", rights)
    write_json("protected_baseline.json", baseline)
    post = protected_fingerprint()
    protected_checks = {
        "baseline_equals_post_generation": baseline == post,
        "main_tex_unchanged": sha256(ROOT / "main.tex")
        == "ecb7c38a12c65c13873b75e7d6032bec1bf0c9d89e3044eb6d158341e4917199",
        "main_sivp_unchanged": sha256(ROOT / "main_sivp_snjnl.tex")
        == "ecb7c38a12c65c13873b75e7d6032bec1bf0c9d89e3044eb6d158341e4917199",
        "submission_gate_passed": False,
        "no_cuda_or_evaluation_work_performed": True,
        "no_manuscript_draft_created": True,
    }
    if not all(value for key, value in protected_checks.items() if key != "submission_gate_passed"):
        raise RuntimeError(f"V68 protected-file check failed: {protected_checks}")
    write_json("protected_postcheck.json", {"fingerprint": post, "checks": protected_checks})
    final = {
        "decision": DECISION,
        "scientific_evidence_valid": True,
        "rights_and_citation_gate_passed": False,
        "manuscript_inclusion": "exclude_from_current_manuscript",
        "appendix_draft_created": False,
        "reason": "Dataset provider/citation/version/license/research-use and aggregate-reporting permissions are incomplete.",
        "evidence_boundary": {
            "descriptive_only": True,
            "matched_seeds": 2,
            "independent_test": False,
            "significance_claim": False,
            "external_generalization_claim": False,
            "calibrated_reliability_claim": False,
        },
        "checks": {
            "frozen_evidence_verified": all(evidence["checks"].values()),
            "arithmetic_reproduced": arithmetic["frozen_v67_comparison_matched"],
            "protected_files_unchanged": protected_checks["baseline_equals_post_generation"],
            "no_cuda": True,
            "no_historical_edits": True,
            "no_active_manuscript_edits": True,
        },
    }
    write_json("final_decision.json", final)
    (OUT / "handoff.md").write_text(
        f"""# V68 Handoff

Decision: `{DECISION}`.

V65-V67 hashes, decisions, safety records, per-seed metrics, matched deltas, means, and sample standard deviations were reproduced exactly. The scientific evidence is valid but remains a two-seed source-train-derived devval stress test with mixed paired AP direction.

MM-UAV cannot enter the current manuscript because provider/release authority, canonical dataset citation, version, dataset license, research-use permission, and aggregate-results reporting permission are unresolved. Code and paper licenses are not dataset grants. No appendix draft was created.

The MM-UAV protocol is not an external replication of the TriAir headline configuration: it uses 320 x 320 inputs, one ordered pass, learned feature alignment, a Softplus bbox-distance path, no modality dropout, and a non-independent devval split, versus the current 640 x 640, 50-epoch TriAir protocol.

Protected production, historical, manuscript, and submission fingerprints remained unchanged. No CUDA, training, evaluation, tuning, or checkpoint selection was performed.
""",
        encoding="utf-8",
    )
    print(json.dumps({"decision": DECISION, "outputs": len(list(OUT.iterdir())), "checks": final["checks"]}, indent=2))


if __name__ == "__main__":
    run()
