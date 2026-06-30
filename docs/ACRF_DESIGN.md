# Availability-Conditioned Reliability Fusion

Availability-Conditioned Reliability Fusion (ACRF) is a targeted extension of the existing Reliability Fusion RepViT-FCOS baseline.

The motivation is specific to the current experiments: under synthetic missing-modality tests, a reliability gate can still allocate nonzero alpha to an absent modality. ACRF corrects that behavior without adding cross-attention, transformer blocks, extra detector heads, or a large parameter increase.

## Input Convention

The model keeps the same TriAir 5-channel input convention:

- RGB: channels `0:3`
- Thermal: channel `3:4`
- Event: channel `4:5`

The availability tensor is shaped `B x 3` in RGB, thermal, event order. A value of `1` means present; `0` means absent.

## ACRF Components

ACRF combines three mechanisms:

- Post-stem availability masking: after each modality stem, the feature map is multiplied by the corresponding availability bit. An absent modality has exact zero post-stem feature energy.
- Masked reliability softmax: unavailable modality logits are set to a very negative value before softmax, forcing absent-modality alpha to be numerically zero.
- Availability-conditioned gate input: the three-bit availability vector is appended to the pooled modality features before the reliability MLP.

## Fallback Availability

For backward compatibility with existing synthetic missing-modality tools, if no availability tensor is supplied the backbone derives availability from exact all-zero modality inputs. This fallback is an evaluation convention, not a general sensor-failure detector.

## Parameter Budget

Compared with E2 reliability fusion, ACRF only expands the first reliability linear layer from 48 to 51 input features. This adds 48 parameters, well below the 0.03M parameter budget.
