# V40 Prohibited Tuning Actions

The following actions are disallowed after this contract is frozen:

- Do not start p=0.20 or any other V40 training until this contract is accepted.
- Do not change V40 v2 train, validation, or guard manifests.
- Do not use the guard partition for model selection or performance reporting.
- Do not change raw data, labels, model code, loader code, trainer core, evaluator core, or prior V38/V39 artifacts.
- Do not use AP, F1, loss, predictions, confidence, checkpoints, or qualitative images to change split or training settings.
- Do not use DroneVehicle or any external data in the V40 evidence pipeline.
- Do not run robustness, profiling, qualitative, manuscript, or submission work under Gate 1.
- Do not selectively retry a weak-scoring run; resolve technical failures only by documented full-contract policy.
- Do not call finish_task.ps1 for V40 master-plan gates.
