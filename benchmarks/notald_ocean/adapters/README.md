# Solver adapter contract

Each benchmark participant will receive the same blinded evaluation problem representation appropriate to its interface, the frozen resource limits, and—only for learning systems—the same permitted lower-resolution tied training bundle.

Principal professional ATP adapters:

- `vampire/`
- `eprover/`
- `iprover/`
- `prover9/`

Optional legacy control:

- `spass/`

Research-system adapters:

- `depths_f/`
- `data_atp/`
- `data_2_0_1/`
- `notald/`

Every adapter must report at least:

- final raw system status;
- path to raw solver output;
- path to any returned certificate;
- whether the independent verifier accepted that certificate;
- charged search work / expansions under the frozen accounting rule;
- wall-clock time;
- peak memory;
- software version and executable hash where available.

The NOTALD adapter additionally records per-role work for P and R, shared-bank events, cross-role reuse, and the first accepted conclusive certificate.

No adapter may read the private answer key, planted shortest route, expected status, `L*`, or target-specific certificate while solving the held-out instance.
