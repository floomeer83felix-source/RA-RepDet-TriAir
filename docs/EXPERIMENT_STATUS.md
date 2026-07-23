# Experiment Status

Updated: 2026-07-23

## Active state

`V67_TWO_SEED_RELIABILITY_FULLTRAIN_COMPLETE`

## V67 completion

V67 completed the frozen MM-UAV matched two-seed reliability-fusion Softplus benchmark. Both runs used the exact V65/V66 seed-specific initializations, the complete 7,187-row frozen order, active V57 shared image-conditioned reliability scoring, and the unchanged Softplus FCOS/evaluator protocol.

- Optimizer steps: `14,374 / 14,374`, exactly `7,187` per seed.
- Diagnostic backward calls: `80 / 80`, exactly `40` per seed.
- Verified recovery snapshots: `38 / 38`; recovery events: `0`.
- Audits: `20 / 20` were `GEOMETRY_AND_GRADIENT_PRESERVED`.
- Evaluation: each final checkpoint was evaluated exactly once on all `1,845` devval images.
- Post-run tests: `10 / 10` passed.
- No tuning, threshold selection, checkpoint selection, extra seed/variant, completed-step rerun, or adaptive extension occurred.

An initial V67 instrumentation launch stopped before the first optimizer step because the diagnostic method was called on the scaffold rather than the detector. The one-line V57 API correction and regression test were source-locked before the formal run. The zero-step attempt did not consume training budget or produce a scientific checkpoint.

## Matched devval results

Seed 0 reliability metrics were AP/AP50/AP75 `0.0404763204 / 0.1567504662 / 0.0056653983` and AR@1/10/100 `0.0518818485 / 0.0829680800 / 0.0890424011`.

Seed 1 reliability metrics were AP/AP50/AP75 `0.0025823958 / 0.0139110456 / 0.0002883784` and AR@1/10/100 `0.0115292997 / 0.0188661267 / 0.0203191996`.

Relative to the matched V65/V66 equal-fusion baselines, AP deltas were `+0.0041719276` for seed 0 and `-0.0004533834` for seed 1. Their mean was `+0.0018592721`, with range `0.0046253111`.

The reliability AP mean/sample standard deviation were `0.0215293581 / 0.0267950511`, again showing substantial initialization sensitivity.

## Fusion evidence

Both scorers departed from exact uniform weights at step 2. On the complete devval set, mean RGB/IR/event weights were:

- seed 0: `0.5550344586 / 0.1881090552 / 0.2568564415`;
- seed 1: `0.5600358248 / 0.1698493063 / 0.2701148987`.

RGB was the largest weight on all 1,845 devval images for both seeds. Weight sums, logits, entropy, losses, gradients, parameters, predictions, and metrics remained finite.

## Evidence boundary

V67 establishes only a matched two-seed devval comparison of equal and image-conditioned reliability fusion under the frozen MM-UAV Softplus protocol. With `n=2`, mixed per-seed AP deltas, and no independent test set, it does not establish statistical significance, broad generalization, or automatic manuscript superiority. No further GPU stage is authorized by V67.
