# V53 Alignment Design

The mechanism is STN-inspired residual affine feature alignment. A zero-initialized residual head makes the initial affine transform exactly identity. `alignment_enabled=False` provides the frozen no-alignment control. Equal and reliability-aware fusion interfaces share the same aligned features.
