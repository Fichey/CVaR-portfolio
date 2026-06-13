"""Optymalizacja portfela akcji z miarą ryzyka CVaR (program liniowy,
formuła Rockafellara-Uryaseva).

Uwaga: w PDF-ie wewnątrz (.)^+ stoi x^T(s_j - S_0), co jest zyskiem,
a nie stratą L_T(x) zdefiniowaną w tym samym dokumencie - to literówka.
Implementujemy wersję spójną z definicją CVaR, tj. x^T(S_0 - s_j).
"""

import cvxpy as cp
import numpy as np


def optimize_portfolio(S0, s, p, r_e, V0=10_000.0, alpha=0.95):
    """Zwraca (x, VaR, CVaR) portfela o minimalnym CVaR_alpha przy zadanej
    oczekiwanej stopie zwrotu r_e, budżecie V0 i zakazie krótkiej sprzedaży.

    S0: ceny początkowe (n,), s: scenariusze cen w T (m, n),
    p: prawdopodobieństwa scenariuszy (m,).
    """
    S0 = np.asarray(S0, dtype=float)
    s = np.asarray(s, dtype=float)
    p = np.asarray(p, dtype=float)
    n = len(S0)
    m = len(p)

    x = cp.Variable(n)
    beta = cp.Variable()    # w optimum beta* = VaR_alpha
    z = cp.Variable(m)      # linearyzacja: w optimum z_j = (L_j(x) - beta)^+

    losses = (S0 - s) @ x

    objective = cp.Minimize(beta + (1.0 / (1.0 - alpha)) * (p @ z))

    constraints = [
        z >= losses - beta,
        z >= 0,
        x @ S0 == V0,
        (p @ ((s - S0) @ x)) / V0 == r_e,
        x >= 0,
    ]

    problem = cp.Problem(objective, constraints)
    problem.solve()

    if problem.status != cp.OPTIMAL:
        raise ValueError(
            f"Nie znaleziono rozwiązania optymalnego (status: {problem.status}). "
            f"Sprawdź, czy stopa zwrotu r_e = {r_e} jest osiągalna."
        )

    return x.value, float(beta.value), float(problem.value)


if __name__ == "__main__":
    from scenario_generator import DEFAULT_S0, generate_scenarios

    V0 = 10_000.0
    alpha = 0.95
    r_e = 0.02

    s, p = generate_scenarios(T=20, m=1000)
    x, var, cvar = optimize_portfolio(DEFAULT_S0, s, p, r_e, V0=V0, alpha=alpha)

    weights = x * DEFAULT_S0 / V0
    print(f"Parametry: V0 = {V0:.0f}, alpha = {alpha}, r_e = {r_e:.1%}")
    print(f"\nOptymalny skład portfela (sztuki):  {x.round(2)}")
    print(f"Wagi kapitałowe portfela:           {weights.round(4)}")
    print(f"Suma wag: {weights.sum():.6f}, wartość portfela: {x @ DEFAULT_S0:.2f}")

    print(f"\nVaR_{alpha}(x)  = beta* = {var:8.2f}")
    print(f"CVaR_{alpha}(x)         = {cvar:8.2f}")

    gains = (s - DEFAULT_S0) @ x
    print(f"\nOczekiwany zwrot portfela: {p @ gains / V0:.4%} (zadane r_e = {r_e:.4%})")
    losses = -gains
    tail = losses[losses > var]
    if tail.size > 0:
        print(f"Empiryczny CVaR (średnia strat > VaR): {tail.mean():.2f}")
