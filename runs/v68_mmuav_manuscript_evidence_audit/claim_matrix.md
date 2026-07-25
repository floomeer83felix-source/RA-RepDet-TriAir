# V68 Claim Matrix

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
