"""Generuje grafiki pomocnicze do prezentacji (spójne z main.py)."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np

from cvar_optimizer import optimize_portfolio
from scenario_generator import _simulate_markov_states, generate_scenarios

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch

OUT = os.path.dirname(os.path.abspath(__file__))

NAVY = "#1E2761"
ICE = "#CADCFC"
RED = "#C0392B"
GREEN = "#2C7A4B"
GRAY = "#6B7280"

V0 = 10_000.0
ALPHA = 0.95
T, M, SEED = 30, 1000, 42
S0 = np.array([100.0, 50.0, 75.0, 120.0, 90.0])
INITIAL_STATES = np.array([0, 0, 1, 1, 2])
P = np.array([[0.90, 0.08, 0.02], [0.10, 0.80, 0.10], [0.02, 0.13, 0.85]])
MU = np.array([0.020, -0.002, -0.022])
SIGMA = np.array([0.025, 0.015, 0.035])
RE_SHOW = 0.1283  # portfel prezentowany w main.py


def fig_trajectories():
    """Trajektorie cen: akcja startująca w hossie vs w bessie."""
    rng = np.random.default_rng(SEED)
    n_paths = 60
    states = _simulate_markov_states(P, np.array([0, 2]), T, n_paths, rng)
    Z = rng.standard_normal((T, n_paths, 2))
    returns = MU[states] + SIGMA[states] * Z
    paths = 100.0 * np.cumprod(1.0 + returns, axis=0)
    paths = np.vstack([np.full((1, n_paths, 2), 100.0), paths])

    fig, ax = plt.subplots(figsize=(8.4, 4.6))
    t = np.arange(T + 1)
    ax.plot(t, paths[:, :, 0], color=GREEN, alpha=0.18, lw=1)
    ax.plot(t, paths[:, :, 1], color=RED, alpha=0.18, lw=1)
    ax.plot(t, paths[:, :, 0].mean(axis=1), color=GREEN, lw=3,
            label="start w hossie (średnia)")
    ax.plot(t, paths[:, :, 1].mean(axis=1), color=RED, lw=3,
            label="start w bessie (średnia)")
    ax.axhline(100, color=GRAY, lw=1, ls="--")
    ax.set_xlabel("krok czasowy t")
    ax.set_ylabel("cena akcji [PLN]")
    ax.set_title(f"{2 * n_paths} symulowanych trajektorii cen (S$_0$ = 100)")
    ax.legend(loc="upper left")
    ax.grid(alpha=0.3)
    ax.set_xlim(0, T)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "trajektorie.png"), dpi=170)
    plt.close(fig)


def fig_loss_histogram():
    """Histogram strat portfela z zaznaczonym VaR i CVaR."""
    s, p = generate_scenarios(S0=S0, transition_matrix=P,
                              initial_states=INITIAL_STATES, mu=MU,
                              sigma=SIGMA, T=T, m=M, seed=SEED)
    x, var, cvar = optimize_portfolio(S0, s, p, RE_SHOW, V0=V0, alpha=ALPHA)
    losses = (S0 - s) @ x

    fig, ax = plt.subplots(figsize=(8.4, 4.6))
    bins = np.linspace(losses.min(), losses.max(), 55)
    ax.hist(losses[losses <= var], bins=bins, color=ICE, edgecolor=NAVY,
            linewidth=0.4, label="straty ≤ VaR (95% przypadków)")
    ax.hist(losses[losses > var], bins=bins, color=RED, edgecolor="#7B241C",
            linewidth=0.4, label="ogon strat > VaR (5% przypadków)")
    ax.axvline(var, color=NAVY, lw=2.5, ls="--")
    ax.axvline(cvar, color=RED, lw=2.5, ls="--")
    ymax = ax.get_ylim()[1]
    dx = 0.015 * (losses.max() - losses.min())
    ax.text(var - dx, ymax * 0.97, f"VaR$_{{0.95}}$ = {var:.0f} PLN",
            color=NAVY, fontweight="bold", va="top", ha="right")
    ax.text(cvar + dx, ymax * 0.80, f"CVaR$_{{0.95}}$ = {cvar:.0f} PLN",
            color=RED, fontweight="bold", va="top")
    ax.set_xlabel("strata portfela L$_T$(x) w scenariuszu [PLN]  (ujemna = zysk)")
    ax.set_ylabel("liczba scenariuszy")
    ax.set_title(f"Rozkład strat optymalnego portfela (m = {M} scenariuszy, "
                 f"r$_e$ = {RE_SHOW:.1%})")
    ax.legend(loc="upper left")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "histogram_strat.png"), dpi=170)
    plt.close(fig)


def fig_markov_diagram():
    """Diagram łańcucha Markova: 3 stany rynku i macierz przejścia."""
    fig, ax = plt.subplots(figsize=(8.0, 4.4))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5.5)
    ax.axis("off")

    pos = {"hossa": (1.8, 3.9), "stagnacja": (5.0, 1.4), "bessa": (8.2, 3.9)}
    colors = {"hossa": GREEN, "stagnacja": GRAY, "bessa": RED}
    self_p = {"hossa": 0.90, "stagnacja": 0.80, "bessa": 0.85}
    R = 0.95

    for name, (cx, cy) in pos.items():
        ax.add_patch(Circle((cx, cy), R, facecolor=colors[name],
                            edgecolor="white", lw=2.5, zorder=3))
        ax.text(cx, cy + 0.16, name.upper(), ha="center", va="center",
                color="white", fontsize=13, fontweight="bold", zorder=4)
        ax.text(cx, cy - 0.30, f"{self_p[name]:.2f}", ha="center", va="center",
                color="white", fontsize=11, zorder=4)

    def arrow(a, b, prob, rad, offset):
        (x1, y1), (x2, y2) = pos[a], pos[b]
        d = np.array([x2 - x1, y2 - y1], dtype=float)
        d /= np.linalg.norm(d)
        start = (x1 + d[0] * R * 1.12, y1 + d[1] * R * 1.12)
        end = (x2 - d[0] * R * 1.12, y2 - d[1] * R * 1.12)
        ax.add_patch(FancyArrowPatch(
            start, end, connectionstyle=f"arc3,rad={rad}",
            arrowstyle="-|>", mutation_scale=16, lw=1.8,
            color=NAVY, zorder=2))
        mx, my = (start[0] + end[0]) / 2 + offset[0], \
                 (start[1] + end[1]) / 2 + offset[1]
        ax.text(mx, my, f"{prob:.2f}", ha="center", va="center",
                fontsize=10.5, color=NAVY, fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.15", fc="white",
                          ec=NAVY, lw=0.8), zorder=5)

    arrow("hossa", "stagnacja", 0.08, 0.25, (-0.55, -0.10))
    arrow("stagnacja", "hossa", 0.10, 0.25, (0.55, -0.35))
    arrow("stagnacja", "bessa", 0.10, 0.25, (-0.55, -0.35))
    arrow("bessa", "stagnacja", 0.13, 0.25, (0.55, -0.10))
    arrow("hossa", "bessa", 0.02, -0.32, (0.0, 0.42))
    arrow("bessa", "hossa", 0.02, -0.32, (0.0, -0.42))

    ax.text(5.0, 5.25, "Liczby = prawdopodobieństwa przejścia w jednym kroku "
            "(w kółkach: pozostanie w stanie)", ha="center", fontsize=10,
            color=GRAY, style="italic")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "diagram_markowa.png"), dpi=170)
    plt.close(fig)


if __name__ == "__main__":
    fig_trajectories()
    fig_loss_histogram()
    fig_markov_diagram()
    print("Zapisano grafiki w:", OUT)
