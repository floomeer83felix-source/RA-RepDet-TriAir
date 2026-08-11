# V84 Gate-Quality Analysis

The primary model family is dynamic gate without training-time modality dropout (seeds 0, 1, and 2). Clean descriptors use 32-bin normalized Shannon entropy, intensity mean/standard deviation, and event nonzero activity. Controlled RGB and thermal corruption is deterministic box blur (kernels 3, 7, 11); event corruption is deterministic attenuation (0.75, 0.50, 0.25). Only one modality changes at a time.

Mean corrupted-modality weights by severity and monotonic checks: `{"event": {"nonincreasing": false, "severity_means": [0.1773386274149218, 0.18913695884475437, 0.19167395672220963, 0.16463007132694887]}, "rgb": {"nonincreasing": false, "severity_means": [0.42240785342761955, 0.4232722353686777, 0.4245810492090754, 0.4252750838012971]}, "thermal": {"nonincreasing": false, "severity_means": [0.40025351915009394, 0.4018866755684484, 0.4037506872211729, 0.40453203444822666]}}`.

The weights are learned task-driven fusion weights, not calibrated physical sensor-health probabilities. Results use exposed development-validation labels; no day/night labels were invented and the locked holdout was not accessed.
