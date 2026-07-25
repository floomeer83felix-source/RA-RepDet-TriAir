"""Run the metadata-only V69 MM-UAV blind-partition preflight."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import subprocess
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "runs/v69_mmuav_zero_shot_external_validation_preflight"
LOCAL = Path(
    os.environ.get(
        "RAREPDET_V69_LOCAL",
        str(Path.home() / "rarepdet_private" / "v69_mmuav_zero_shot_preflight"),
    )
)
LOCAL_LEDGER = LOCAL / "historical_exposure_ledger.csv"
START_COMMIT = "744650efe4f6daff3cf2d07a07ae52e3e51638d1"
DECISION = "V69_BLOCKED_NO_UNUSED_MMUAV_PARTITION"

SOURCES = {
    "v52_sequence_alignment": (
        "runs/v52_mmuav_audit/sequence_alignment.csv",
        "57d60fe9ea19aa1de8e2ff7f95c33f8579d8b544598ae9526c5d62c217deb4c9",
    ),
    "v52_directory_inventory": (
        "runs/v52_mmuav_audit/directory_inventory.csv",
        "cf9d353b632ebb588a1268449c61f3d10e212bcde558ec309fe3baad4a54626f",
    ),
    "v52_train_sampled": (
        "runs/v52_mmuav_audit/manifests/train_sampled.txt",
        "9feee0e362a6885dd9ba68a4dd9a903c6ee3dc459be04a9699d725a9184582d1",
    ),
    "v52_devval_sampled": (
        "runs/v52_mmuav_audit/manifests/devval_sampled.txt",
        "88a2f32000b2c3b1b9cb5021916a29e55df73e46daeaf22f537c854488aa8800",
    ),
    "v52_dataset_audit": (
        "runs/v52_mmuav_audit/dataset_audit.json",
        "3c4782aa7d5f83ec9205d1a73065bcb11e35b734796b939f3bcd5b721faae0b3",
    ),
    "v52_sampling_protocol": (
        "runs/v52_mmuav_audit/sampling_protocol.json",
        "3d410e812874b29f0688b2d24bcac781192c883264daba598be596b649c89e65",
    ),
    "v53_train_supervised": (
        "runs/v53_mmuav_feature_alignment_preflight/manifests/train_rgb_supervised.txt",
        "e81973b95dd6fd5ce2d3c5de526310a3bef083df49b8db584fdf39b78a34d67a",
    ),
    "v53_devval_supervised": (
        "runs/v53_mmuav_feature_alignment_preflight/manifests/devval_rgb_supervised.txt",
        "113c304794cb32232ca4121edcd8fd8f40dab5a540b2d52b1f165ac4adb37a54",
    ),
    "v53_preflight": (
        "runs/v53_mmuav_feature_alignment_preflight/preflight_result.json",
        "4b424715b34d34626cbbf693cd6a7e91c1a4f668f1f11777005dab643d12df55",
    ),
    "v68_decision": (
        "runs/v68_mmuav_manuscript_evidence_audit/final_decision.json",
        "8926c3f776309f626a6d8f77b10d4c9a95cba8b40d08dec64291d5057e319a5e",
    ),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def read_json(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def write_json(name: str, payload: object) -> None:
    (OUT / name).write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def read_tsv(relative: str) -> list[dict[str, str]]:
    with (ROOT / relative).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def read_csv(relative: str) -> list[dict[str, str]]:
    with (ROOT / relative).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def dataset_root() -> Path:
    text = (ROOT / "docs/PROJECT_CONTEXT.md").read_text(encoding="utf-8")
    match = re.search(r"MM-UAV private research subset root:\s*`?([^`\r\n]+)", text)
    if not match:
        raise RuntimeError("MM-UAV root is missing from project context")
    return Path(match.group(1).strip())


def protected_paths() -> list[Path]:
    historical = re.compile(r"^runs/v(?:4[0-9]|5[0-9]|6[0-8])_")
    fixed = {
        "rarepdet/train_early_fusion.py",
        "rarepdet/models/early_fusion_fcos.py",
        "rarepdet/models/reliability_fusion_fcos.py",
        "datasets/triair_dataset.py",
        "main.tex",
        "main_sivp_snjnl.tex",
    }
    selected: list[Path] = []
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


def verify_sources() -> dict[str, object]:
    records = {}
    for key, (relative, expected) in SOURCES.items():
        actual = sha256(ROOT / relative)
        records[key] = {
            "path": relative,
            "expected_sha256": expected,
            "actual_sha256": actual,
            "match": actual == expected,
        }
    v52 = read_json(SOURCES["v52_dataset_audit"][0])
    v68 = read_json(SOURCES["v68_decision"][0])
    checks = {
        "all_hashes_match": all(record["match"] for record in records.values()),
        "v52_complete_sequences": v52["complete_train_sequences"] == 424,
        "v52_triplets": v52["synchronized_triplets"] == 897578,
        "v52_only_partial_source_train": "partial source-train extraction"
        in " ".join(v52["limitations"]).lower(),
        "v68_rights_still_blocked": v68["decision"] == "V68_BLOCKED_DATA_RIGHTS_OR_CITATION_INCOMPLETE",
    }
    if not all(checks.values()):
        raise RuntimeError(f"V69 source evidence mismatch: {checks}")
    return {"records": records, "checks": checks}


def build_exposure_sets() -> tuple[set[tuple[str, int]], set[tuple[str, int]]]:
    sampled: set[tuple[str, int]] = set()
    development: set[tuple[str, int]] = set()
    for key in ("v52_train_sampled", "v52_devval_sampled"):
        sampled.update(
            (row["sequence"], int(row["frame_index"])) for row in read_tsv(SOURCES[key][0])
        )
    for key in ("v53_train_supervised", "v53_devval_supervised"):
        development.update(
            (row["sequence"], int(row["frame_index"])) for row in read_tsv(SOURCES[key][0])
        )
    if len(sampled) != 45036 or len(development) != 9032 or not development.issubset(sampled):
        raise RuntimeError("V69 exposure row contract mismatch")
    return sampled, development


def inventory_metadata(sequence_rows: list[dict[str, str]]) -> dict[str, object]:
    root = dataset_root()
    if not root.is_dir():
        raise RuntimeError("Configured MM-UAV subset root is unavailable")
    actual_sequences = {path.name for path in root.iterdir() if path.is_dir()}
    expected_sequences = {row["sequence"] for row in sequence_rows}
    parent_entries = sorted(path.name for path in root.parent.iterdir())
    checks = {
        "sequence_identity_match": actual_sequences == expected_sequences,
        "sequence_count": len(actual_sequences) == 424,
        "only_provider_train_split_present": root.name.lower() == "train"
        and "test" not in {name.lower() for name in parent_entries},
        "all_sequence_indices_exact": all(row["exact_filename_index_match"] == "True" for row in sequence_rows),
        "all_modal_counts_match": all(
            row["rgb_count"] == row["ir_count"] == row["event_count"] for row in sequence_rows
        ),
    }
    if not all(checks.values()):
        raise RuntimeError(f"V69 identity-only inventory mismatch: {checks}")
    return {
        "inventory_mode": "identity_metadata_only",
        "provider_split_names_present": [root.name],
        "complete_sequence_count": len(actual_sequences),
        "synchronized_triplet_count": sum(int(row["rgb_count"]) for row in sequence_rows),
        "native_modality_schema_from_frozen_v52": {
            "rgb": "640x360",
            "ir": "640x512",
            "event": "346x260",
        },
        "candidate_media_opened": False,
        "candidate_labels_opened": False,
        "checks": checks,
    }


def write_local_ledger(
    sequence_rows: list[dict[str, str]],
    sampled: set[tuple[str, int]],
    development: set[tuple[str, int]],
) -> dict[str, object]:
    LOCAL.mkdir(parents=True, exist_ok=False)
    development_sequences = {sequence for sequence, _ in development}
    if len(development_sequences) != 424:
        raise RuntimeError(f"Expected all 424 sequences to be development-linked, got {len(development_sequences)}")
    counts: Counter[str] = Counter()
    with LOCAL_LEDGER.open("w", encoding="utf-8", newline="") as handle:
        fields = [
            "opaque_sample_id",
            "provider_split",
            "sequence",
            "frame_index",
            "direct_exposure",
            "sequence_exposure",
            "blind_eligible",
            "exclusion_reason",
        ]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in sorted(sequence_rows, key=lambda item: item["sequence"]):
            sequence = row["sequence"]
            frame_max = int(row["index_max"])
            for frame in range(1, frame_max + 1):
                identity = (sequence, frame)
                if identity in development:
                    exposure = "DEVELOPMENT_USED"
                elif identity in sampled:
                    exposure = "CONTENT_EXPOSED"
                else:
                    exposure = "IDENTITY_ONLY"
                counts[exposure] += 1
                writer.writerow(
                    {
                        "opaque_sample_id": hashlib.sha256(
                            f"provider-train:{sequence}:{frame}".encode()
                        ).hexdigest()[:24],
                        "provider_split": "train",
                        "sequence": sequence,
                        "frame_index": frame,
                        "direct_exposure": exposure,
                        "sequence_exposure": "DEVELOPMENT_USED",
                        "blind_eligible": "False",
                        "exclusion_reason": "SAME_SEQUENCE_AS_DEVELOPMENT_USED",
                    }
                )
    total = sum(counts.values())
    if total != 897578:
        raise RuntimeError(f"V69 full-ledger row mismatch: {total}")
    return {
        "local_only": True,
        "committed": False,
        "rows": total,
        "sha256": sha256(LOCAL_LEDGER),
        "bytes": LOCAL_LEDGER.stat().st_size,
        "direct_exposure_counts": dict(sorted(counts.items())),
        "sequence_exposure": {"DEVELOPMENT_USED": 424},
        "blind_eligible_rows": 0,
        "contains_absolute_paths": False,
        "contains_media_or_labels": False,
    }


def write_blocked_stage_records() -> None:
    blocked = {
        "status": "NOT_ATTEMPTED_UPSTREAM_NO_UNUSED_PARTITION",
        "reason": "V69 stops after the blind-partition gate; no downstream contract may imply readiness.",
    }
    write_json("candidate_blind_manifest_metadata.json", {
        **blocked,
        "candidate_exists": False,
        "row_count": 0,
        "sequence_count": 0,
        "full_manifest_created": False,
    })
    (OUT / "candidate_manifest_sha256.txt").write_text(
        "NOT_CREATED_NO_ELIGIBLE_PARTITION\n", encoding="utf-8"
    )
    write_json("label_seal_record.json", {
        **blocked,
        "candidate_annotation_files_hashed": False,
        "candidate_labels_parsed": False,
        "seal_created": False,
    })
    write_json("triair_checkpoint_manifest.json", blocked)
    write_json("triair_checkpoint_verification.json", {
        **blocked,
        "checkpoint_files_opened": 0,
        "strict_load_attempts": 0,
    })
    write_json("triair_model_contract.json", blocked)
    (OUT / "mmuav_to_triair_adapter_spec.md").write_text(
        "# Adapter Status\n\nNot frozen because V69 failed at the earlier unused-partition gate. No candidate-informed adapter work occurred.\n",
        encoding="utf-8",
    )
    write_json("mmuav_to_triair_adapter_spec.json", {
        **blocked,
        "parameter_free_adapter_frozen": False,
        "candidate_informed_choices": False,
    })
    write_json("adapter_source_lock.json", blocked)
    write_json("adapter_determinism_tests.json", {
        **blocked,
        "tests_run": 0,
    })
    write_json("class_ontology_mapping.json", {
        **blocked,
        "mapping_frozen": False,
        "candidate_labels_inspected": False,
    })
    write_json("zero_shot_evaluator_contract.json", {
        **blocked,
        "evaluator_frozen": False,
        "candidate_inference_attempts": 0,
        "candidate_metric_computations": 0,
    })


def write_narrative() -> None:
    (OUT / "protocol.md").write_text(
        """# V69 MM-UAV Zero-Shot External Validation Preflight

V69 is metadata-only and follows a strict gate order:

1. verify immutable V52-V68 evidence;
2. build a complete sample/sequence exposure ledger;
3. discover an untouched official split or wholly unexposed sequence component;
4. only if step 3 succeeds, verify TriAir checkpoints and freeze adapter/evaluator/labels.

The local provider material contains 424 complete sequences under the provider train split and no source test split. Historical V52 interval-20 records cover all 424 sequences, and V53-V67 development rows cover every sequence. The same-sequence exclusion rule therefore makes all 897,578 synchronized local triplets ineligible. V69 stops at step 3 without opening candidate media or labels and without checkpoint inference.
""",
        encoding="utf-8",
    )
    (OUT / "historical_exposure_ledger_schema.md").write_text(
        """# Historical Exposure Ledger Schema

The full ledger is local-only and contains one row per synchronized provider-train triplet.

| Field | Meaning |
|---|---|
| opaque_sample_id | One-way identifier derived from provider split, sequence, and frame identity |
| provider_split | Provider split identity; only `train` is locally present |
| sequence / frame_index | Identity metadata, not content |
| direct_exposure | `DEVELOPMENT_USED`, `CONTENT_EXPOSED`, or `IDENTITY_ONLY` |
| sequence_exposure | Maximum historical exposure of the linked sequence |
| blind_eligible | False for every local row |
| exclusion_reason | `SAME_SEQUENCE_AS_DEVELOPMENT_USED` |

`DEVELOPMENT_USED` covers the 9,032 V53 supervised rows used by V54-V67. `CONTENT_EXPOSED` covers the remaining V52 interval-20 rows whose annotation/content-derived metadata was audited. Other frames are `IDENTITY_ONLY` directly, but remain ineligible because all 424 sequences contain development-used rows.
""",
        encoding="utf-8",
    )
    (OUT / "rights_and_reporting_boundary.md").write_text(
        """# Rights And Reporting Boundary

- `internal_scientific_protocol_ready`: false, because no unused local MM-UAV partition exists.
- `manuscript_reporting_ready`: false, independently, because V68 remains blocked on provider authority, canonical citation, version, dataset license/access terms, research-use permission, aggregate-reporting permission, and redistribution terms.

The rights blocker neither authorizes MM-UAV training nor changes the scientific independence rules. The no-partition blocker neither resolves nor weakens the publication-rights restriction.
""",
        encoding="utf-8",
    )


def run() -> None:
    if git("rev-parse", "HEAD") != START_COMMIT:
        raise RuntimeError(f"Unexpected V69 starting commit: {git('rev-parse', 'HEAD')}")
    if OUT.exists() or LOCAL.exists():
        raise RuntimeError("V69 output or local ledger directory already exists")
    baseline = protected_fingerprint()
    OUT.mkdir(parents=True)
    source_verification = verify_sources()
    sequence_rows = read_csv(SOURCES["v52_sequence_alignment"][0])
    if len(sequence_rows) != 424:
        raise RuntimeError("V69 sequence ledger does not contain 424 complete sequences")
    sampled, development = build_exposure_sets()
    inventory = inventory_metadata(sequence_rows)
    ledger = write_local_ledger(sequence_rows, sampled, development)
    sampled_sequences = {sequence for sequence, _ in sampled}
    development_sequences = {sequence for sequence, _ in development}
    sequence_audit = {
        "provider_train_sequences": 424,
        "v52_sampled_sequences": len(sampled_sequences),
        "v53_v67_development_used_sequences": len(development_sequences),
        "wholly_unexposed_sequences": 0,
        "same_sequence_exclusion_applied": True,
        "eligible_sequences": 0,
        "checks": {
            "v52_covers_all_sequences": len(sampled_sequences) == 424,
            "development_covers_all_sequences": len(development_sequences) == 424,
            "all_inventory_sequences_linked": all(
                row["sequence"] in development_sequences for row in sequence_rows
            ),
        },
    }
    discovery = {
        "discovery_mode": "identity_metadata_only",
        "official_splits_locally_present": inventory["provider_split_names_present"],
        "official_test_split_present": False,
        "provider_train_sequences": 424,
        "wholly_unexposed_sequence_components": 0,
        "eligible_candidate_rows": 0,
        "candidate_selected": False,
        "labels_read": False,
        "media_opened": False,
        "predictions_generated": False,
        "metrics_computed": False,
        "decision": DECISION,
    }
    duplicate_audit = {
        "candidate_exists": False,
        "sample_overlap_test": "NOT_APPLICABLE_NO_CANDIDATE",
        "sequence_overlap_test": "BLOCKED_ALL_424_SEQUENCES_DEVELOPMENT_LINKED",
        "exact_content_duplicate_test": "NOT_RUN_NO_CANDIDATE",
        "near_duplicate_test": "NOT_RUN_NO_CANDIDATE",
        "candidate_content_hashed_or_decoded": False,
        "conclusion": "No candidate remains after the stronger sequence-level exclusion gate.",
    }
    write_narrative()
    write_json("source_evidence_verification.json", source_verification)
    write_json("historical_exposure_ledger_summary.json", ledger)
    write_json("full_inventory_metadata.json", inventory)
    write_json("candidate_partition_discovery.json", discovery)
    write_json("sequence_component_independence_audit.json", sequence_audit)
    write_json("exact_and_near_duplicate_audit.json", duplicate_audit)
    write_blocked_stage_records()
    protocol = {
        "starting_commit": START_COMMIT,
        "task": "V69_MMUAV_ZERO_SHOT_EXTERNAL_VALIDATION_PROTOCOL_AND_BLIND_TEST_FREEZE",
        "mode": "cpu_metadata_only",
        "gate_order": [
            "source_evidence",
            "exposure_ledger",
            "candidate_partition",
            "triair_checkpoints",
            "adapter",
            "evaluator",
            "label_seal",
        ],
        "stopped_after_gate": "candidate_partition",
        "cuda_work": False,
        "training_or_adaptation": False,
        "candidate_inference": False,
        "candidate_label_inspection": False,
        "candidate_metrics": False,
    }
    write_json("protocol.json", protocol)
    (OUT / "test_commands.txt").write_text(
        "C:\\Users\\xinnan\\.conda\\envs\\pytorch\\python.exe rarepdet/tools/run_v69_mmuav_zero_shot_preflight.py\n"
        "C:\\Users\\xinnan\\.conda\\envs\\pytorch\\python.exe -m unittest discover -s tests -p test_v69_mmuav_zero_shot_preflight.py -v\n",
        encoding="utf-8",
    )
    source_lock_paths = [
        "rarepdet/tools/run_v69_mmuav_zero_shot_preflight.py",
        "tests/test_v69_mmuav_zero_shot_preflight.py",
        *[relative for relative, _ in SOURCES.values()],
    ]
    write_json("source_lock.json", {
        "starting_commit": START_COMMIT,
        "sources": {
            relative: {"sha256": sha256(ROOT / relative)}
            for relative in source_lock_paths
        },
    })
    post = protected_fingerprint()
    protected = {
        "baseline": baseline,
        "post": post,
        "checks": {
            "unchanged": baseline == post,
            "no_cuda": True,
            "no_candidate_content_access": True,
            "no_private_or_heavy_git_output": True,
        },
    }
    if not all(protected["checks"].values()):
        raise RuntimeError(f"V69 protected-file audit failed: {protected['checks']}")
    write_json("protected_file_audit.json", protected)
    final = {
        "decision": DECISION,
        "internal_scientific_protocol_ready": False,
        "manuscript_reporting_ready": False,
        "candidate_partition_exists": False,
        "reason": "All 424 locally available provider-train sequences are linked to V53-V67 development-used rows, and no local official test split exists.",
        "counts": {
            "local_synchronized_triplets": 897578,
            "direct_development_used": ledger["direct_exposure_counts"]["DEVELOPMENT_USED"],
            "direct_content_exposed": ledger["direct_exposure_counts"]["CONTENT_EXPOSED"],
            "direct_identity_only_but_sequence_ineligible": ledger["direct_exposure_counts"]["IDENTITY_ONLY"],
            "development_linked_sequences": 424,
            "eligible_sequences": 0,
            "eligible_rows": 0,
        },
        "downstream_not_attempted": {
            "triair_checkpoint_verification": True,
            "adapter_freeze": True,
            "evaluator_freeze": True,
            "label_seal": True,
        },
        "checks": {
            "source_evidence_verified": all(source_verification["checks"].values()),
            "complete_sample_ledger": ledger["rows"] == 897578,
            "complete_sequence_ledger": len(sequence_rows) == 424,
            "no_candidate_inference": True,
            "no_candidate_label_inspection": True,
            "no_cuda_or_training": True,
            "protected_files_unchanged": protected["checks"]["unchanged"],
        },
    }
    write_json("final_decision.json", final)
    (OUT / "handoff.md").write_text(
        f"""# V69 Handoff

Decision: `{DECISION}`.

The complete local metadata ledger contains 897,578 synchronized provider-train triplets across 424 sequences. V52 interval-20 records cover every sequence. The 9,032 V53 supervised rows used by V54-V67 also cover every sequence. Therefore every local sequence is linked to `DEVELOPMENT_USED` content, and all remaining directly identity-only frames are ineligible under the same-sequence rule.

Only the provider train split is locally available; V52 already recorded that no source test split was present. No random resplit, old train/devval relabeling, candidate media/label inspection, inference, or metric computation occurred.

V69 stopped at the candidate-partition gate. TriAir checkpoint verification, five-channel adapter freeze, evaluator freeze, and label sealing were not attempted because completing them could not produce an eligible blind test. V68 publication rights remain independently blocked.
""",
        encoding="utf-8",
    )
    print(json.dumps({
        "decision": DECISION,
        "ledger_rows": ledger["rows"],
        "ledger_sha256": ledger["sha256"],
        "eligible_sequences": 0,
        "eligible_rows": 0,
    }, indent=2))


if __name__ == "__main__":
    run()
