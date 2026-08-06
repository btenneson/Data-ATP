"""Reproduce the five figures used in the Hilbert budget paper."""
from pathlib import Path
import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch

OUT = Path(__file__).with_name("figures")
OUT.mkdir(exist_ok=True)


def _rot(n, x, y, rx, ry):
    if ry == 0:
        if rx == 1:
            x, y = n - 1 - x, n - 1 - y
        x, y = y, x
    return x, y


def hilbert_points(order):
    n = 2**order
    pts = []
    for d in range(n*n):
        x = y = 0
        t, s = d, 1
        while s < n:
            rx = 1 & (t // 2)
            ry = 1 & (t ^ rx)
            x, y = _rot(s, x, y, rx, ry)
            x, y = x + s*rx, y + s*ry
            t //= 4
            s *= 2
        pts.append(((x + 0.5)/n, (y + 0.5)/n))
    return np.asarray(pts)


def fig_2d():
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.8))
    p = hilbert_points(4)
    axes[0].plot(p[:, 0], p[:, 1])
    axes[0].set_title("Finite Hilbert approximant (level 4)")
    for q, style in zip((1, 2, 3), ("--", "-.", "-")):
        p = hilbert_points(q)
        if q % 2 == 0:
            p = p[::-1]
        axes[1].plot(p[:, 0], p[:, 1], linestyle=style, label=f"level {q}")
    axes[1].set_title("Complete coarse-to-fine passes")
    axes[1].legend()
    for ax in axes:
        ax.set_aspect("equal"); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    fig.tight_layout(); fig.savefig(OUT/"fig1_2d_hilbert.png", dpi=220); plt.close(fig)


def fig_partial():
    fig, ax = plt.subplots(figsize=(7, 6))
    n = 4
    for i in range(n+1):
        ax.plot([i/n, i/n], [0, 1], linewidth=.5)
        ax.plot([0, 1], [i/n, i/n], linewidth=.5)
    coarse = hilbert_points(2)
    ax.plot(coarse[:, 0], coarse[:, 1], linewidth=2)
    r = math.sqrt(2)/(2*n)
    for x, y in coarse:
        ax.add_patch(Circle((x, y), r, fill=False, alpha=.2))
    fine = hilbert_points(3)[:24]
    ax.plot(fine[:, 0], fine[:, 1]); ax.scatter(*fine[-1], marker="x")
    ax.set_aspect("equal"); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.set_title("Interrupted refinement retains coarse guarantee")
    fig.tight_layout(); fig.savefig(OUT/"fig2_2d_partial.png", dpi=220); plt.close(fig)


def fig_3d():
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection="3d")
    previous = None
    for j in range(5):
        p = hilbert_points(2)
        if j % 2:
            p = p[::-1]
        z = np.full(len(p), j/4)
        if previous is not None:
            ax.plot([previous[0], p[0, 0]], [previous[1], p[0, 1]], [previous[2], z[0]])
        ax.plot(p[:, 0], p[:, 1], z)
        previous = (p[-1, 0], p[-1, 1], z[-1])
    ax.set_title("Layered 3D traversal")
    fig.tight_layout(); fig.savefig(OUT/"fig3_3d_layered.png", dpi=220); plt.close(fig)


def fig_directions():
    fig, ax = plt.subplots(figsize=(9, 5.5)); ax.axis("off")
    c = np.array([.28, .5])
    for angle, label in zip(np.linspace(0, 2*np.pi, 8, endpoint=False),
                            ("+e1", "+e2", "+e3", "+e4", "-e1", "-e2", "-e3", "-e4")):
        end = c + .2*np.array([math.cos(angle), math.sin(angle)])
        ax.add_patch(FancyArrowPatch(c, end, arrowstyle="-|>", mutation_scale=14))
        ax.text(*(end + .04*np.array([math.cos(angle), math.sin(angle)])), label, ha="center")
    ax.text(.68, .66, r"$|\mathcal{D}_n|=2n$", fontsize=18, ha="center")
    ax.text(.68, .42, r"nonreverse choices $=2n-1$", fontsize=16, ha="center")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    fig.tight_layout(); fig.savefig(OUT/"fig4_ndirections.png", dpi=220); plt.close(fig)


def fig_atp():
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.8))
    ax = axes[0]
    for i in range(5):
        ax.plot([i/4, i/4], [0, 1], linewidth=.5); ax.plot([0, 1], [i/4, i/4], linewidth=.5)
    coarse = np.array([[.25, .25], [.25, .75], [.75, .75], [.75, .25]])
    ax.plot(coarse[:, 0], coarse[:, 1], "-o")
    fine = hilbert_points(2)[:10]; ax.plot(fine[:, 0], fine[:, 1], "-x")
    ax.set_aspect("equal"); ax.set_title("Proof-state feature coverage")
    B = np.logspace(1, 5, 200)
    for d in (2, 3, 5):
        axes[1].loglog(B, B**(-1/d), label=f"d={d}")
    axes[1].set_title("Ideal expansion-budget law"); axes[1].legend()
    fig.tight_layout(); fig.savefig(OUT/"fig5_atp_budget.png", dpi=220); plt.close(fig)


if __name__ == "__main__":
    fig_2d(); fig_partial(); fig_3d(); fig_directions(); fig_atp()
