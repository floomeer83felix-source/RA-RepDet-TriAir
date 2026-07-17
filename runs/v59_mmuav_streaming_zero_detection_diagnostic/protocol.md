# V59 Streaming Diagnostic Protocol

Three read-only 1,845-row passes in frozen order. CPU int64 histograms use 16,384 frozen bins; only bounded per-image arrays receive exact quantiles. Optimizer, backward, gradients, training mode, metric replay, and repair are forbidden.
