# Private answer-key area

Actual generated answer keys, planted routes, independently audited shortest paths, and target-specific certificates must **not** be committed here and must never be mounted into a solver-visible working directory during a scored run.

This directory exists only to document the separation boundary.

For a real run, keep private scoring material in a separate local or CI-controlled location. The runner should pass only opaque instance identifiers to the solver process and join them back to the private scoring record after the solver has stopped.

The repository may remain private, but repository privacy is not a substitute for solver-process blinding: a solver being benchmarked must still be unable to inspect answer-bearing files.
