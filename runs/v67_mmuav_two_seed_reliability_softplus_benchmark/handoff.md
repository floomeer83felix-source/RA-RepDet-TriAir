# V67 Handoff

Decision: `V67_TWO_SEED_RELIABILITY_FULLTRAIN_COMPLETE`.

## Frozen contracts

- Starting commit: `2d79d722b93ef4206527e2bef531bafa370c4b95`.
- Authorization base / V66 completion: `70a54d92b8deb8cb9a0f748230731cddad641d9f`.
- Train/devval rows: `7,187 / 1,845`; manifest SHA256 values `e81973b95dd6fd5ce2d3c5de526310a3bef083df49b8db584fdf39b78a34d67a` and `113c304794cb32232ca4121edcd8fd8f40dab5a540b2d52b1f165ac4adb37a54`.
- Frozen order SHA256: `27e98f752d4707c862c41495420cd1776a9095ad0a010becff2035deef0bf27b`.
- Seed-0/seed-1 initialization SHA256: `846da59cc8d908dfeb429fca2acb4985e73ff5fda3915154f9f764c571977cb9` / `50612d58789b935ed8345494a7830a64d07b83c841ac9b6d24bcda3ea3f2c476`.
- Sole intervention: V57 `alignment_on_reliability_superset` instead of `alignment_on_equal_superset`.
- Softplus bbox activation: `beta=1.0`, `threshold=20.0`; optimizer, model, data, order, audits, recovery, and evaluator matched V65/V66.

## CPU and source gates

For each seed, reliability and equal models had identical parameter names, tensors, buffers, and state dictionaries. At step 0, active reliability weights were exact uniform `[1/3, 1/3, 1/3]`; aligned/fused features, pre-activation bbox logits, classification logits, centerness logits, losses, and decoded predictions were bit-identical. The scorer received finite nonzero gradients on the first backward gate.

An initial CUDA instrumentation launch stopped before optimizer step 1 because `fusion_diagnostics()` was called on the scaffold rather than the detector. The method call and regression test were corrected and source-locked before formal execution. The zero-step attempt produced no scientific checkpoint or evaluation and consumed no optimizer-step budget.

## Training and audits

- Steps: `14,374 / 14,374`, exactly `7,187` per seed in frozen order.
- Audits: all `20 / 20` were `GEOMETRY_AND_GRADIENT_PRESERVED`.
- Diagnostic backward calls: `80 / 80`.
- Verified recovery snapshots: `38 / 38`; recovery events: `0`.
- Scorer departure from exact uniform: step `2` for both seeds.
- Training elapsed: seed 0 `4,065.659 s`; seed 1 `3,823.605 s`.
- Mean step time: seed 0 `0.531867 s`; seed 1 `0.495370 s`.
- Peak allocated/reserved CUDA bytes: seed 0 `475,608,576 / 511,705,088`; seed 1 `593,417,728 / 645,922,816`.

## Final-checkpoint devval results

| Metric | Equal seed 0 | Reliability seed 0 | Delta | Equal seed 1 | Reliability seed 1 | Delta |
|---|---:|---:|---:|---:|---:|---:|
| AP | 0.0363043928 | 0.0404763204 | +0.0041719276 | 0.0030357792 | 0.0025823958 | -0.0004533834 |
| AP50 | 0.1493416683 | 0.1567504662 | +0.0074087979 | 0.0174066630 | 0.0139110456 | -0.0034956174 |
| AP75 | 0.0035733839 | 0.0056653983 | +0.0020920143 | 0.0003960396 | 0.0002883784 | -0.0001076613 |
| AR@1 | 0.0501429252 | 0.0518818485 | +0.0017389233 | 0.0109337780 | 0.0115292997 | +0.0005955217 |
| AR@10 | 0.0753692234 | 0.0829680800 | +0.0075988566 | 0.0180323964 | 0.0188661267 | +0.0008337303 |
| AR@100 | 0.0815388280 | 0.0890424011 | +0.0075035731 | 0.0195569319 | 0.0203191996 | +0.0007622677 |

Reliability AP mean/sample standard deviation/minimum/maximum/range were `0.0215293581 / 0.0267950511 / 0.0025823958 / 0.0404763204 / 0.0378939246`. The matched AP-delta mean/minimum/maximum/range were `+0.0018592721 / -0.0004533834 / +0.0041719276 / 0.0046253111`.

Each final checkpoint was evaluated once on `1,845` images and `4,198` GT boxes. Each produced `184,500` finite predictions, with zero zero-prediction or non-finite-prediction images.

## Fusion diagnostics

- Seed 0 devval RGB/IR/event mean weights: `0.5550344586 / 0.1881090552 / 0.2568564415`; entropy mean `0.9897606969`.
- Seed 1 devval RGB/IR/event mean weights: `0.5600358248 / 0.1698493063 / 0.2701148987`; entropy mean `0.9792278409`.
- RGB was dominant on all 1,845 devval images for both seeds.
- Weight-sum maximum absolute error was `1.1920929e-07` for both seeds; weights, logits, entropy, gradients, parameters, predictions, and metrics were finite.

## Local authoritative checkpoints

- Seed 0: `D:\MM-UAV_v67_local\v67_seed0_reliability_softplus_b1_t20_fulltrain_final_step7187.pt`; SHA256 `ee26713f7f448c5afacd3e32dc03585836ea90ea50156ebcf540684f415b932a`; `27,146,705` bytes.
- Seed 1: `D:\MM-UAV_v67_local\v67_seed1_reliability_softplus_b1_t20_fulltrain_final_step7187.pt`; SHA256 `7f1c8c807490edfc1f738b6145051b0cc6fc7159a3abec09ad45587bb9aa211d`; `27,146,705` bytes.

Heavy checkpoints, optimizer states, recovery snapshots, tensors, and raw predictions remain local and outside Git.

## Evidence boundary

Post-run tests passed `10 / 10`. V67 is a matched two-seed devval comparison only. The mixed per-seed AP deltas, large seed spread, `n=2`, and lack of an independent test set do not support statistical significance, broad generalization, or automatic manuscript superiority. No tuning, threshold/checkpoint selection, extra seed/variant, completed-step rerun, or extension occurred.
