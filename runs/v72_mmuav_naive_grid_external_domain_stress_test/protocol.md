# V72 Naive-Grid External-Domain Stress Test

Scientific label: `zero-shot external-domain stress test on the exposed MM-UAV devval split using a naive normalized-grid five-channel adapter`.

RGB, IR, and event are decoded and independently letterboxed to 640 x 640 using the frozen V53 implementation, then concatenated as five channels. RGB annotation geometry is retained. This normalized-grid assumption does not establish physical cross-modal pixel registration.
