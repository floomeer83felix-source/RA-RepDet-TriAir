# V85 Deterministic Selection Protocol

All 2,213 frozen development-validation samples are described before inference. Scene A uses RGB luminance at or above the linear 75th percentile and at least two GT boxes; Scene B uses luminance at or below the 25th percentile and at least two boxes. Each minimizes distance to its bucket median GT count, then sample ID. Scene C uses GT count at or above the linear 90th percentile and minimizes distance to bucket median RGB luminance, then sample ID. Later scenes skip components already selected. No model output participates.
