# V68 Manuscript Inclusion Recommendation

## Recommendation

Exclude MM-UAV evidence from the current manuscript and keep V65-V67 internal until the data-rights and citation record is complete.

## Rationale

The metrics are reproducible and the matched design is useful as an internal stress test, but the paired AP direction is mixed and initialization sensitivity is large. The protocol also differs materially from the current TriAir headline configuration: 320 x 320 rather than 640 x 640, one ordered pass rather than 50 epochs, learned feature alignment, a Softplus bbox-distance path, no modality dropout, and source-train-derived devval rather than an external independent test.

More importantly, the provider, canonical citation, dataset version, dataset license, research-use grant, and aggregate-results reporting permission remain unresolved. That is a hard submission blocker independent of scientific strength. No appendix draft is created under the V68 contract.

## Reconsideration checklist

1. Obtain provider-verifiable canonical citation and dataset version.
2. Preserve the dataset license or access terms.
3. Confirm research use and publication of aggregate derived metrics are permitted.
4. Record redistribution restrictions explicitly.
5. Re-run this documentary gate without changing V65-V67 results.
