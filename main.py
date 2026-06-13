"""Główny skrypt projektu: scenariusze z łańcucha Markova + optymalizacja
CVaR w pętli po siatce r_e -> granica efektywna i skład wybranego portfela.

Uruchomienie:  python main.py
"""

import numpy as np

# cvar_optimizer (cvxpy) musi być importowany PRZED matplotlib.pyplot:
# przy uszkodzonej instalacji cupy (zbudowanej pod numpy 1.x) próbkowanie
# solverów GPU przez cvxpy po załadowaniu matplotliba kończy się segfaultem.
from cvar_optimizer import optimize_portfolio
from scenario_generator import STATE_NAMES, generate_scenarios

import matplotlib.pyplot as plt

V0 = 10_000.0
ALPHA = 0.95
T = 30
M = 1000
SEED = 42

S0 = np.array([100.0, 50.0, 75.0, 120.0, 90.0])

#: Stany początkowe akcji (0 = hossa, 1 = stagnacja, 2 = bessa).
INITIAL_STATES = np.array([0, 0, 1, 1, 2])

#: Duża trwałość stanów -> oczekiwane zwroty akcji rozpinają ok. -7%..+21%,
#: dzięki czemu cały docelowy zakres analizy r_e od 2% do 15% jest osiągalny.
TRANSITION_MATRIX = np.array(
    [
        # hossa  stagnacja  bessa
        [0.90,   0.08,      0.02],
        [0.10,   0.80,      0.10],
        [0.02,   0.13,      0.85],
    ]
)

MU = np.array([0.020, -0.002, -0.022])
SIGMA = np.array([0.025, 0.015, 0.035])

RE_MIN_TARGET = 0.02
RE_MAX_TARGET = 0.15
N_GRID = 25

#: r_e portfela prezentowanego na wykresie kołowym (na efektywnej gałęzi).
RE_PIE = 0.13

STOCK_LABELS = [
    f"Akcja {i + 1} (start: {STATE_NAMES[state]})"
    for i, state in enumerate(INITIAL_STATES)
]


def achievable_return_range(S0, s, p):
    """Zwraca (min, max, wektor) oczekiwanych zwrotów akcji; przy x >= 0
    i pełnym budżecie zwrot portfela to kombinacja wypukła zwrotów akcji."""
    expected_returns = p @ ((s - S0) / S0)
    return expected_returns.min(), expected_returns.max(), expected_returns


def compute_efficient_frontier(S0, s, p, r_targets):
    """Liczy optymalne portfele dla siatki r_e; zwraca słownik z kluczami
    're', 'cvar', 'var', 'x' (tylko punkty osiągalne)."""
    results = {"re": [], "cvar": [], "var": [], "x": []}
    for r_e in r_targets:
        try:
            x, var, cvar = optimize_portfolio(S0, s, p, r_e, V0=V0, alpha=ALPHA)
        except ValueError:
            print(f"  r_e = {r_e:6.2%}  -> nieosiągalne (problem niedopuszczalny)")
            continue
        results["re"].append(r_e)
        results["cvar"].append(cvar)
        results["var"].append(var)
        results["x"].append(x)
        print(f"  r_e = {r_e:6.2%}  ->  CVaR = {cvar:9.2f},  VaR = {var:9.2f}")
    return results


def plot_efficient_frontier(results, pie_idx, filename="granica_efektywna.png"):
    """Rysuje granicę efektywną CVaR: ryzyko (oś X) vs zwrot (oś Y)."""
    cvar = np.array(results["cvar"])
    re = np.array(results["re"])

    # Portfel o minimalnym CVaR dzieli krzywą na gałąź zdominowaną i efektywną.
    i_min = int(np.argmin(cvar))

    fig, ax = plt.subplots(figsize=(9, 6))
    ax.plot(cvar[: i_min + 1], 100 * re[: i_min + 1], "o--", color="tab:gray",
            lw=1.5, ms=5, label="Portfele nieefektywne (zdominowane)")
    ax.plot(cvar[i_min:], 100 * re[i_min:], "o-", color="tab:blue", lw=2,
            ms=5, label="Granica efektywna CVaR")
    ax.plot(cvar[i_min], 100 * re[i_min], "s", color="tab:green", ms=11,
            label=f"Portfel o minimalnym CVaR ($r_e$ = {re[i_min]:.2%})")
    ax.plot(cvar[pie_idx], 100 * re[pie_idx], "*", color="tab:red", ms=18,
            label=f"Wybrany portfel ($r_e$ = {re[pie_idx]:.2%})")

    ax.set_title(f"Granica efektywna: CVaR$_{{{ALPHA}}}$ vs oczekiwana stopa zwrotu\n"
                 f"(n = 5 akcji, m = {M} scenariuszy, T = {T}, V$_0$ = {V0:.0f})")
    ax.set_xlabel(f"Ryzyko: CVaR$_{{{ALPHA}}}$ straty portfela [PLN]")
    ax.set_ylabel("Oczekiwana stopa zwrotu $r_e$ [%]")
    ax.grid(True, alpha=0.4)
    ax.legend(loc="upper right")
    fig.tight_layout()
    fig.savefig(filename, dpi=150)
    print(f"Zapisano wykres: {filename}")


def plot_portfolio_pie(x, S0, r_e, cvar, filename="portfel_kolowy.png"):
    """Rysuje wykres kołowy wag kapitałowych optymalnego portfela."""
    weights = x * S0 / V0

    # Rozwiązania LP są wierzchołkowe, więc część wag jest dokładnie zerowa.
    nonzero = weights > 1e-6
    shown_weights = weights[nonzero]
    shown_labels = [lab for lab, keep in zip(STOCK_LABELS, nonzero) if keep]

    fig, ax = plt.subplots(figsize=(9, 6))
    wedges, _, _ = ax.pie(
        shown_weights,
        autopct="%1.1f%%",
        startangle=90,
        colors=plt.cm.tab10.colors,
        wedgeprops={"edgecolor": "white", "linewidth": 1.5},
    )
    ax.legend(wedges, shown_labels, title="Skład portfela",
              loc="center left", bbox_to_anchor=(1.0, 0.5))
    ax.set_title(f"Wagi kapitałowe optymalnego portfela dla $r_e$ = {r_e:.1%}\n"
                 f"(CVaR$_{{{ALPHA}}}$ = {cvar:.2f} PLN, akcje o wadze 0 pominięto)")
    fig.tight_layout()
    fig.savefig(filename, dpi=150)
    print(f"Zapisano wykres: {filename}")


def main():
    print("=" * 70)
    print("KROK 1: Generowanie scenariuszy rynkowych (łańcuch Markova)")
    print("=" * 70)
    s, p = generate_scenarios(
        S0=S0, transition_matrix=TRANSITION_MATRIX,
        initial_states=INITIAL_STATES, mu=MU, sigma=SIGMA,
        T=T, m=M, seed=SEED,
    )
    print(f"Wygenerowano m = {M} scenariuszy cen {len(S0)} akcji na T = {T} kroków.")

    r_lo, r_hi, asset_returns = achievable_return_range(S0, s, p)
    print("\nOczekiwane stopy zwrotu akcji:")
    for label, r in zip(STOCK_LABELS, asset_returns):
        print(f"  {label:28s} {r:7.2%}")
    print(f"Osiągalny zakres r_e portfela (bez krótkiej sprzedaży): "
          f"[{r_lo:.2%}, {r_hi:.2%}]")

    print("\n" + "=" * 70)
    print(f"KROK 2: Optymalizacja CVaR (alpha = {ALPHA}, V0 = {V0:.0f})")
    print("=" * 70)
    eps = 1e-4
    grid_lo = max(RE_MIN_TARGET, r_lo + eps)
    grid_hi = min(RE_MAX_TARGET, r_hi - eps)
    if grid_lo >= grid_hi:
        # Docelowy zakres nie przecina się z osiągalnym - bierzemy osiągalny.
        grid_lo, grid_hi = r_lo + eps, r_hi - eps
    r_targets = np.linspace(grid_lo, grid_hi, N_GRID)
    print(f"Siatka r_e: {N_GRID} punktów w zakresie [{grid_lo:.2%}, {grid_hi:.2%}]")

    results = compute_efficient_frontier(S0, s, p, r_targets)

    print("\n" + "=" * 70)
    print("KROK 3: Wykresy")
    print("=" * 70)
    pie_idx = int(np.argmin(np.abs(np.array(results["re"]) - RE_PIE)))
    x_pie = results["x"][pie_idx]
    re_pie = results["re"][pie_idx]
    cvar_pie = results["cvar"][pie_idx]

    plot_efficient_frontier(results, pie_idx)
    plot_portfolio_pie(x_pie, S0, re_pie, cvar_pie)

    print(f"\nPrezentowany portfel (r_e = {re_pie:.2%}):")
    weights = x_pie * S0 / V0
    for label, xi, wi in zip(STOCK_LABELS, x_pie, weights):
        print(f"  {label:28s} {xi:8.2f} szt.  (waga {wi:6.2%})")
    print(f"  VaR_{ALPHA}  = {results['var'][pie_idx]:.2f} PLN")
    print(f"  CVaR_{ALPHA} = {cvar_pie:.2f} PLN")

    plt.show()


if __name__ == "__main__":
    main()
