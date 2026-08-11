# Current Task

## Active task

`V84_JEI_CRITICAL_EXPERIMENT_CLOSURE_PLANNED`

Codex should execute the plan in:

```text
docs/CODEX_V84_JEI_CRITICAL_EXPERIMENTS_PLAN.md
```

V83 fixed-hardware efficiency evidence is complete. The V81 checkpoint-backed single-modality weights remain the authoritative single-modality source. Historical V77/V80 supplied rows remain reconciliation-only.

## Immediate Codex execution order

1. **P0 — preflight:** freeze repository state, split identities, and exact V48/V81 checkpoint inventory.
2. **P1 — train RGB+Thermal baseline:** seeds 0/1/2, same component-disjoint split, same training/evaluator contract, no selective reruns.
3. **P2 — matched 2×2 analysis:** evaluate early/no-dropout, early/dropout, gate/no-dropout, gate/dropout under all/RGB-removed/thermal-removed/event-removed conditions for seeds 0/1/2.
4. **P3 — gate-quality analysis:** export clean gate weights, compute reproducible modality-quality descriptors, and run controlled single-modality corruption sweeps using gate-no-dropout as the primary model.
5. **P4 — component-cluster bootstrap:** use leakage-graph components as the resampling unit for the primary paired comparisons.
6. **P5 — published comparator:** reproduce one official TriAir representative method or another credible public multimodal detector on the exact same split/evaluator. Stop transparently if code/license/protocol incompatibility prevents a valid comparison.
7. **P6 — optional core seed extension:** if compute remains, add seeds 3/4 only for matched early and gate-no-dropout.
8. **P7 — MM-UAV reproducibility closure:** document sequence manifests, tracking-to-detection conversion, alignment architecture, transfer matching rule, and evaluation protocol; do not rerun training by default.
9. **P8 — manuscript integration:** only after evidence freeze; define RA-RepDet as the dynamic gate, make gate-no-dropout the nominal-accuracy primary variant if supported, and treat modality dropout as an optional robustness regularizer.

## Highest-priority scientific questions

V84 must answer these questions directly:

- Does event information add value beyond an RGB+Thermal model trained without event input?
- How much of missing-modality robustness comes from the dynamic gate versus modality-dropout training?
- Do learned modality weights respond systematically to controlled degradation and measurable input quality?
- Does dynamic gating remain stronger than static/deterministic fusion under component-aware uncertainty analysis?
- Is RA-RepDet competitive with at least one published multimodal method under the exact same split and evaluator?

## Frozen scientific positioning

- `RA-RepDet` = sample-dependent / input-conditioned dynamic modality gating.
- Modality dropout is an optional robustness regularizer, not the core fusion mechanism.
- Gate/no-dropout currently has the strongest nominal AP among the six causal variants (`0.7251 ± 0.0121`).
- Gate+dropout currently has lower nominal AP (`0.7156 ± 0.0172`) and must not be presented as the best-performing default solely because it was previously treated as the full system.
- Reliability weights are learned task-driven modality weights/proxies, not calibrated physical sensor-health probabilities.
- No SOTA claim, no physical sensor-failure claim, and no statistical-significance claim from three seeds alone.

## Locked-holdout protection

The 837-image internal holdout remains **locked**.

Codex must **stop before any holdout access**. Reuse requires a separate explicit author instruction specifically authorizing `837-image locked holdout reuse` after the final V84 model/comparator/evaluator choices are frozen.

Do not inspect holdout labels, regenerate holdout metrics, tune on the holdout, or use holdout results to choose a model.

## Expected V84 output root

```text
runs/v84_jei_critical_closure/
```

The final evidence summary must be written to:

```text
runs/v84_jei_critical_closure/V84_EVIDENCE_SUMMARY.md
```

and must state which manuscript claims are strengthened, weakened, or unchanged.

## Completion gate

Do not mark V84 complete until:

- RGB+Thermal seeds 0/1/2 are complete;
- matched channel-removal analysis is complete or a missing-checkpoint limitation is documented;
- gate-quality/corruption evidence is complete;
- component-cluster bootstrap is complete;
- one published comparator is complete or a documented reproducibility/license stop reason exists;
- MM-UAV reproducibility documentation is complete;
- no locked-holdout access occurred;
- manuscript integration happens only after evidence freeze.

## Previous completed work

V83 completed checkpoint integrity and fixed RTX-3090 efficiency benchmarking for 15 verified checkpoints. It did not materially improve the stronger efficiency table already present in the manuscript, so no accuracy evidence was changed.

Commit activating this task:

```text
docs: activate V84 JEI critical experiment closure
```

## Commit Message

experiments: complete V84 JEI critical evidence closure
