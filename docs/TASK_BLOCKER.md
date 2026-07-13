# Task Blocker

Status: `V50_BLOCKED_TEST_ACCESS_ORDER_VIOLATION`

Generated: 2026-07-13T19:58:03+08:00

## Exact blocker

The frozen V50 source lock states that the test partition is inaccessible before all three dataset-specific RGB checkpoints and evaluator settings are frozen. The local execution order violated that rule:

- `2026-07-13T19:23:05+08:00`: V50 source lock generated.
- `2026-07-13T19:35:11+08:00`: first zero-shot test result generated.
- `2026-07-13T19:47:52+08:00`: last zero-shot test result generated.
- `2026-07-13T19:56:22+08:00`: RGB seed 0 training started; seeds 1 and 2 remained pending.
- `2026-07-13T19:58:03+08:00`: queue PID `13148` and training PID `22216` were stopped after the violation was detected.
- `2026-07-13T20:06:33+08:00`: a concurrent process used `--continue-after-protocol-violation` without an explicit user instruction authorizing a scope amendment.
- `2026-07-13T20:13:22+08:00`: second queue PID `48068` and training PID `64948` were stopped; seed 0 had reached epoch 1 iteration 1618/1618 but no checkpoint existed.

No RGB checkpoint had been frozen when test access began. `rgb_run_status.json` additionally recorded `test_accessed=false` even though test result artifacts already existed. The test partition can no longer satisfy the preregistered blind-test ordering, so the existing test metrics are quarantined as protocol-violation evidence and are not accepted V50 final results.

The later exploratory continuation is also quarantined. Its `continuation_authorized_at` field did not correspond to any explicit user authorization, and it does not repair the earlier test access.

Machine-readable evidence: `runs/v50_visdrone_seen/protocol_violation_evidence.json`.

## Last 50 error/execution lines

There was no Python exception: the failure is a scientific protocol gate, and `rgb_queue_launcher_stderr.log` is empty (`0` bytes). The training log contained only the following 30 lines when the process was stopped; these are all available lines and therefore the complete last-up-to-50-line record:

```text
requested_seed: 0
deterministic_algorithms: warn_only
cudnn_deterministic: True
cudnn_benchmark: False
device: cuda
train samples: 6471
val samples: 548
params: 6591603
iterations per epoch: 1618
epoch 1/50 iter 1/1618 loss=2.8915 mean_loss=2.8915
epoch 1/50 iter 20/1618 loss=2.4425 mean_loss=2.3599
epoch 1/50 iter 40/1618 loss=2.1821 mean_loss=2.2837
epoch 1/50 iter 60/1618 loss=2.1032 mean_loss=2.2203
epoch 1/50 iter 80/1618 loss=2.0008 mean_loss=2.1821
epoch 1/50 iter 100/1618 loss=2.0389 mean_loss=2.1519
epoch 1/50 iter 120/1618 loss=1.7862 mean_loss=2.1054
epoch 1/50 iter 140/1618 loss=1.8095 mean_loss=2.0656
epoch 1/50 iter 160/1618 loss=1.8747 mean_loss=2.0289
epoch 1/50 iter 180/1618 loss=1.7173 mean_loss=2.0001
epoch 1/50 iter 200/1618 loss=1.7935 mean_loss=1.9768
epoch 1/50 iter 220/1618 loss=1.6426 mean_loss=1.9587
epoch 1/50 iter 240/1618 loss=1.6635 mean_loss=1.9382
epoch 1/50 iter 260/1618 loss=1.6528 mean_loss=1.9205
epoch 1/50 iter 280/1618 loss=1.6347 mean_loss=1.9030
epoch 1/50 iter 300/1618 loss=1.6582 mean_loss=1.8883
epoch 1/50 iter 320/1618 loss=1.6359 mean_loss=1.8751
epoch 1/50 iter 340/1618 loss=1.6907 mean_loss=1.8653
epoch 1/50 iter 360/1618 loss=1.6325 mean_loss=1.8576
epoch 1/50 iter 380/1618 loss=1.6293 mean_loss=1.8472
epoch 1/50 iter 400/1618 loss=1.5937 mean_loss=1.8360
```

The first validation invocation used a package-style module path even though `tests/` is not a Python package. Its complete error tail was:

```text
ERROR: test_v50_visdrone_seen (unittest.loader._FailedTest)
----------------------------------------------------------------------
ImportError: Failed to import test module: test_v50_visdrone_seen
Traceback (most recent call last):
  File "C:\Users\xinnan\.conda\envs\pytorch\lib\unittest\loader.py", line 154, in loadTestsFromName
    module = __import__(module_name)
ModuleNotFoundError: No module named 'tests.test_v50_visdrone_seen'

----------------------------------------------------------------------
Ran 1 test in 0.000s

FAILED (errors=1)
```

This command-only error was repaired by using discovery: `python -m unittest discover -s tests -p 'test_v50_visdrone_seen.py' -v`; all 3 tests passed.

The unauthorized continuation ended with the following final five training lines; no weight or checkpoint file was created:

```text
epoch 1/50 iter 1540/1618 loss=1.3273 mean_loss=1.5946
epoch 1/50 iter 1560/1618 loss=1.3876 mean_loss=1.5917
epoch 1/50 iter 1580/1618 loss=1.6136 mean_loss=1.5893
epoch 1/50 iter 1600/1618 loss=1.4711 mean_loss=1.5870
epoch 1/50 iter 1618/1618 loss=1.3166 mean_loss=1.5854
```

## Attempted checks and containment

1. Re-read `AGENTS.md`, `docs/NEXT_TASK.md`, and the frozen `source_lock_v50` test-access rule.
2. Verified raw result timestamps and hashes against the RGB queue start time.
3. Confirmed seed 0 had no frozen checkpoint and seeds 1/2 had not started.
4. Stopped both the queue parent and training child processes and confirmed both PIDs exited.
5. Preserved all audit, source-lock, raw-result, status, and training-log contradictions without deleting or rewriting the frozen source lock.
6. Did not access TriAir holdout data, modify raw VisDrone-SEEN files, fabricate modalities, or edit the manuscript.
7. Verified all 8 source-locked code hashes, 6 checkpoint hashes, and 3 manifest hashes; all matched. Corrected the unit-test invocation to discovery and obtained 3/3 passing tests.
8. Detected and stopped an unapproved exploratory continuation, verified that it produced no checkpoint, and removed the CLI bypass in favor of a hard protocol-block gate.
9. Executed the corrected queue entry point against the blocked status and obtained the expected `RuntimeError: V50 is blocked by a test-access-order violation; this frozen task has no continuation override`; no training process started.

`PROJECT_PROFILE.md`, requested by `docs/NEXT_TASK.md`, is also absent at repository root; this is recorded as secondary evidence but is not the primary blocker.

## Related files

- `docs/NEXT_TASK.md`
- `runs/v50_visdrone_seen/source_lock_v50.md`
- `runs/v50_visdrone_seen/source_lock_v50.json`
- `runs/v50_visdrone_seen/protocol_violation_evidence.md`
- `runs/v50_visdrone_seen/protocol_violation_evidence.json`
- `runs/v50_visdrone_seen/rgb_run_status.json`
- `runs/v50_visdrone_seen/rgb_training/seed0/train_log.txt`
- `runs/v50_visdrone_seen/raw/zero_shot/test/**`

## Repair options

1. Provide a fresh, untouched evaluation partition (or a separately source-locked external dataset), then start a new versioned recovery task that freezes all three RGB checkpoints before any access to that partition.
2. Amend the protocol through external review to downgrade the current test partition to post-hoc exploratory evidence, retain only devval for model development, and explicitly abandon any blind-test claim for V50.

Minimal user action required: choose one repair option. The current V50 task cannot honestly be marked complete under its frozen acceptance criteria.

## Separate prior blocker

The V49 Springer/BibTeX compile and rendered-page inspection remains pending independently and was not altered during V50.
