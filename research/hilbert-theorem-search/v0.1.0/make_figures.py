#!/usr/bin/env python3
"""Regenerate the four explanatory figures for release 0.1.0.

Run `python assemble_source.py` first. Requires matplotlib.
"""

from __future__ import annotations

from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

from hilbert_theorem_search import HilbertCurve

OUT = Path(__file__).resolve().parent / "figures"
OUT.mkdir(exist_ok=True)


def figure_1() -> None:
    points = list(HilbertCurve(dimension=2, bits=4).points())
    x = [p[0] for p in points]
    y = [p[1] for p in points]
    fig, ax = plt.subplots(figsize=(7.2, 7.2))
    ax.plot(x, y, linewidth=1)
    ax.scatter([x[0], x[-1]], [y[0], y[-1]], s=35)
    ax.annotate("start", (x[0], y[0]), xytext=(6, 6), textcoords="offset points")
    ax.annotate("end", (x[-1], y[-1]), xytext=(6, 6), textcoords="offset points")
    ax.set_title("Finite 2D Hilbert Approximant: 256 Cells")
    ax.set_xlabel("Premise-slot coordinate 1")
    ax.set_ylabel("Premise-slot coordinate 2")
    ax.set_aspect("equal")
    ax.grid(True, linewidth=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "figure_1_hilbert_2d.png", dpi=220)
    plt.close(fig)


def figure_2() -> None:
    points = list(HilbertCurve(dimension=3, bits=2).points())
    x = [p[0] for p in points]
    y = [p[1] for p in points]
    z = [p[2] for p in points]
    fig = plt.figure(figsize=(7.8, 6.5))
    ax = fig.add_subplot(111, projection="3d")
    ax.plot(x, y, z, linewidth=1.2)
    ax.scatter([x[0], x[-1]], [y[0], y[-1]], [z[0], z[-1]], s=35)
    ax.set_title("Finite 3D Hilbert Approximant: 64 Cells")
    ax.set_xlabel("Premise slot 1")
    ax.set_ylabel("Premise slot 2")
    ax.set_zlabel("Premise slot 3")
    fig.tight_layout()
    fig.savefig(OUT / "figure_2_hilbert_3d.png", dpi=220)
    plt.close(fig)


def figure_3() -> None:
    fig, ax = plt.subplots(figsize=(10, 5.8))
    ax.axis("off")
    boxes = [
        (0.06, 0.57, 0.23, 0.22, "Unary component\nC¹\nrule r₁(a)"),
        (0.38, 0.57, 0.23, 0.22, "Binary component\nC²\nrule r₂(a,b)"),
        (0.70, 0.57, 0.23, 0.22, "Ternary component\nC³\nrule r₃(a,b,c)"),
    ]
    for x, y, w, h, text in boxes:
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02"))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=12)
    ax.text(0.5, 0.90, "Intrinsic search space:  C¹ ⊔ C² ⊔ C³", ha="center", fontsize=16)
    ax.text(
        0.5,
        0.43,
        "Rules are tagged and searched separately; unrelated premise coordinates never form a meaningless product.",
        ha="center",
        fontsize=11,
    )
    ax.add_patch(FancyBboxPatch((0.20, 0.10), 0.60, 0.18, boxstyle="round,pad=0.02"))
    ax.text(0.5, 0.19, "Optional orthogonal embedding in [0,1]ᴷ,  K = 1 + 2 + 3 = 6", ha="center", fontsize=13)
    for x in (0.175, 0.495, 0.815):
        ax.add_patch(FancyArrowPatch((x, 0.57), (0.5, 0.28), arrowstyle="-|>", mutation_scale=13))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    fig.tight_layout()
    fig.savefig(OUT / "figure_3_coproduct.png", dpi=220)
    plt.close(fig)


def figure_4() -> None:
    fig, ax = plt.subplots(figsize=(12, 5.8))
    ax.axis("off")
    labels = [
        "Frozen verified\ntheorem set Cₑ",
        "Rule component\nCₑᵏ",
        "Finite k-D\nHilbert order",
        "Candidate\npremise tuple",
        "Rule application\n+ legality",
        "Independent\nverifier",
        "New theorem-point\n+ proof provenance",
    ]
    xs = [0.02, 0.16, 0.30, 0.44, 0.58, 0.72, 0.86]
    for x, label in zip(xs, labels, strict=True):
        ax.add_patch(FancyBboxPatch((x, 0.47), 0.11, 0.20, boxstyle="round,pad=0.02"))
        ax.text(x + 0.055, 0.57, label, ha="center", va="center", fontsize=10)
    for left, right in zip(xs[:-1], xs[1:], strict=True):
        ax.add_patch(FancyArrowPatch((left + 0.11, 0.57), (right, 0.57), arrowstyle="-|>", mutation_scale=12))
    ax.add_patch(
        FancyArrowPatch(
            (0.915, 0.47),
            (0.075, 0.35),
            connectionstyle="arc3,rad=-0.22",
            arrowstyle="-|>",
            mutation_scale=13,
        )
    )
    ax.text(0.50, 0.24, "Commit only after the frozen epoch; then begin Cₑ₊₁ = D_F(Cₑ).", ha="center", fontsize=12)
    ax.text(0.50, 0.87, "Hilbert Space Filling Curve-Style Theorem Search", ha="center", fontsize=17)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    fig.tight_layout()
    fig.savefig(OUT / "figure_4_pipeline.png", dpi=220)
    plt.close(fig)


def main() -> None:
    figure_1()
    figure_2()
    figure_3()
    figure_4()
    print(f"Wrote figures to {OUT}")


if __name__ == "__main__":
    main()
