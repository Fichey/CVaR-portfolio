"""Moduł optymalizacji portfela akcji z miarą ryzyka CVaR.

Implementuje zadanie optymalizacyjne z dokumentu projektu: minimalizację
CVaR_alpha straty portfela na skończonej przestrzeni probabilistycznej
(m scenariuszy cen s_j z prawdopodobieństwami p_j), korzystając z formuły
Rockafellara-Uryaseva:

    min_{beta, x}  beta + 1/(1-alpha) * sum_j p_j * (L_j(x) - beta)^+

gdzie L_j(x) = -(V_T - V_0) = x^T (S_0 - s_j) to strata portfela
w j-tym scenariuszu.

Uwaga: w PDF-ie wewnątrz (.)^+ stoi x^T(s_j - S_0), co jest zyskiem,
a nie stratą L_T(x) zdefiniowaną w tym samym dokumencie - to literówka.
Implementujemy wersję spójną z definicją CVaR (strata ze znakiem
poprawnym), tj. x^T(S_0 - s_j).

Wyrażenie (L_j(x) - beta)^+ jest nieliniowe, ale wypukłe i kawałkami
liniowe, więc problem linearyzujemy klasycznie: wprowadzamy zmienne
pomocnicze z_j >= 0 z ograniczeniem z_j >= L_j(x) - beta. W minimum
z_j = (L_j(x) - beta)^+, a całość staje się programem liniowym (LP).

Ograniczenia:
    x^T S_0 = V_0                                   (budżet),
    (1/V_0) * sum_j p_j x^T (s_j - S_0) = r_e       (oczekiwana stopa zwrotu),
    x >= 0                                          (zakaz krótkiej sprzedaży).
"""

import cvxpy as cp
import numpy as np


def optimize_portfolio(S0, s, p, r_e, V0=10_000.0, alpha=0.95):
    """Wyznacza portfel o minimalnym CVaR przy zadanej stopie zwrotu.

    Rozwiązuje program liniowy:

        min_{x, beta, z}  beta + 1/(1-alpha) * p^T z
        p.o.  z_j >= x^T (S_0 - s_j) - beta,  j = 1..m   (linearyzacja (.)^+),
              z_j >= 0,
              x^T S_0 = V_0,
              (1/V_0) * sum_j p_j x^T (s_j - S_0) = r_e,
              x >= 0.

    Parameters
    ----------
    S0 : np.ndarray
        Wektor (n,) cen początkowych akcji.
    s : np.ndarray
        Tablica (m, n) scenariuszy cen w momencie T (s[j] = s_j).
    p : np.ndarray
        Wektor (m,) prawdopodobieństw scenariuszy (sumujący się do 1).
    r_e : float
        Wymagana oczekiwana stopa zwrotu portfela na moment T
        (np. 0.02 = 2%).
    V0 : float
        Kapitał początkowy do zainwestowania.
    alpha : float
        Poziom istotności CVaR (0 < alpha < 1, zwykle 0.95).

    Returns
    -------
    x : np.ndarray
        Wektor (n,) optymalnego składu portfela (liczby sztuk akcji).
    var : float
        Optymalne beta* = VaR_alpha(x) portfela.
    cvar : float
        Minimalna wartość CVaR_alpha(x) (optymalna wartość funkcji celu).

    Raises
    ------
    ValueError
        Gdy solver nie znajdzie rozwiązania optymalnego (np. zadana stopa
        zwrotu r_e jest nieosiągalna i problem jest niedopuszczalny).
    """
    S0 = np.asarray(S0, dtype=float)
    s = np.asarray(s, dtype=float)
    p = np.asarray(p, dtype=float)
    n = len(S0)
    m = len(p)

    # Zmienne decyzyjne.
    x = cp.Variable(n)      # skład portfela (liczby sztuk akcji)
    beta = cp.Variable()    # próg strat; w optimum beta* = VaR_alpha
    z = cp.Variable(m)      # zmienne pomocnicze, z_j = (L_j(x) - beta)^+

    # Straty portfela w scenariuszach: L_j(x) = x^T (S_0 - s_j).
    losses = (S0 - s) @ x

    # Funkcja celu: beta + 1/(1-alpha) * sum_j p_j z_j.
    objective = cp.Minimize(beta + (1.0 / (1.0 - alpha)) * (p @ z))

    constraints = [
        z >= losses - beta,                      # linearyzacja (L_j - beta)^+
        z >= 0,
        x @ S0 == V0,                            # budżet
        (p @ ((s - S0) @ x)) / V0 == r_e,        # oczekiwana stopa zwrotu
        x >= 0,                                  # zakaz krótkiej sprzedaży
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
    r_e = 0.02  # wymagane 2% oczekiwanego zwrotu na horyzoncie T

    s, p = generate_scenarios(T=20, m=1000)
    x, var, cvar = optimize_portfolio(DEFAULT_S0, s, p, r_e, V0=V0, alpha=alpha)

    weights = x * DEFAULT_S0 / V0  # udziały kapitału zainwestowane w akcje
    print(f"Parametry: V0 = {V0:.0f}, alpha = {alpha}, r_e = {r_e:.1%}")
    print(f"\nOptymalny skład portfela (sztuki):  {x.round(2)}")
    print(f"Wagi kapitałowe portfela:           {weights.round(4)}")
    print(f"Suma wag: {weights.sum():.6f}, wartość portfela: {x @ DEFAULT_S0:.2f}")

    print(f"\nVaR_{alpha}(x)  = beta* = {var:8.2f}")
    print(f"CVaR_{alpha}(x)         = {cvar:8.2f}")

    # Weryfikacja: oczekiwany zwrot portfela i empiryczny CVaR z definicji.
    gains = (s - DEFAULT_S0) @ x
    print(f"\nOczekiwany zwrot portfela: {p @ gains / V0:.4%} (zadane r_e = {r_e:.4%})")
    losses = -gains
    tail = losses[losses > var]
    if tail.size > 0:
        print(f"Empiryczny CVaR (średnia strat > VaR): {tail.mean():.2f}")
