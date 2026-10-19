# M* GitHub integration: free standard runners

This M* 0.9 **automation starter** lives in an isolated public-repository directory. It is not a new general-purpose ATP, nor evidence of a general exponential-to-linear speedup.

## Automated checks

The [M* 0.9 GitHub Actions workflow](../../.github/workflows/mstar-09-autopilot.yml) runs the full M* autopilot on **ubuntu-latest**, Python 3.12, using an unprivileged `contents: read` token.

It triggers on this folder/workflow changing, or when GitHub accepts a manual dispatch once the workflow is on the default branch. It does **not** run continuously, use any paid larger runner, use secrets, upload artifacts, deploy, or merge. Standard hosted runner minutes on public repositories are free according to GitHub's billing documentation (as checked October 2026); the repository owner should still review current GitHub policies. Logs contain the machine-readable report summary and human-readable report; generated files are not persisted as Actions artifacts.

## Local checks

From the repo root:

```sh
python research/mstar_0_9/autopilot.py --mode full --output /tmp/mstar-09-report
```

Windows: extract/copy this directory and run `AUTOPILOT_WINDOWS.cmd` inside it.

## Scientific claim gates

Passing CI establishes only that the frozen v0.8 baseline and current candidate pass the automated local verification tests. It does not certify the prover as general-purpose or validate an exponential-to-linear algorithmic improvement against competent comparison solvers. Preserve original source files and required independent verification checks.

No automatic branch merges or version promotions are configured.
