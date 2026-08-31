#!/usr/bin/env python3
"""Reproducible launcher for DATA-MIND 2.6 95% set.mm pretraining."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import data_mind_2_6_setmm95_pretrain as TRAIN


def safe_load_module(path: Path):
    spec = importlib.util.spec_from_file_location("dm26_mlsic_pretrain", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import ML-SIC module from {path}")
    mod = importlib.util.module_from_spec(spec)
    # dataclasses resolves annotations through sys.modules during execution.
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


TRAIN.load_module = safe_load_module

if __name__ == "__main__":
    raise SystemExit(TRAIN.main())
