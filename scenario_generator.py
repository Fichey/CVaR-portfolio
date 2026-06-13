"""Generator scenariuszy rynkowych: łańcuch Markova (regime-switching)
+ symulacja Monte Carlo cen akcji.

    S_{t+1} = S_t * (1 + mu(stan) + sigma(stan) * Z),   Z ~ N(0, 1).
"""

import numpy as np

STATE_NAMES = ("hossa", "stagnacja", "bessa")

#: P[i, j] = P(stan_{t+1} = j | stan_t = i).
DEFAULT_TRANSITION_MATRIX = np.array(
    [
        # hossa  stagnacja  bessa
        [0.80,   0.15,      0.05],
        [0.20,   0.60,      0.20],
        [0.05,   0.25,      0.70],
    ]
)

DEFAULT_MU = np.array([0.008, 0.000, -0.010])
DEFAULT_SIGMA = np.array([0.015, 0.010, 0.025])
DEFAULT_S0 = np.array([100.0, 50.0, 75.0, 120.0, 90.0])
DEFAULT_INITIAL_STATES = np.array([0, 0, 1, 1, 2])


def _validate_transition_matrix(transition_matrix):
    """Sprawdza, czy macierz jest poprawną macierzą stochastyczną."""
    P = np.asarray(transition_matrix)
    if P.ndim != 2 or P.shape[0] != P.shape[1]:
        raise ValueError("Macierz przejścia musi być kwadratowa.")
    if np.any(P < 0):
        raise ValueError("Macierz przejścia nie może mieć elementów ujemnych.")
    if not np.allclose(P.sum(axis=1), 1.0):
        raise ValueError("Wiersze macierzy przejścia muszą sumować się do 1.")


def _simulate_markov_states(transition_matrix, initial_states, T, m, rng):
    """Zwraca tablicę (T, m, n) stanów rynku: states[t, j, i] to stan
    i-tej akcji w j-tym scenariuszu po t+1 krokach."""
    n = len(initial_states)
    cum_P = np.cumsum(transition_matrix, axis=1)

    states = np.empty((T, m, n), dtype=np.int64)
    current = np.broadcast_to(initial_states, (m, n)).copy()
    for t in range(T):
        # Próbkowanie metodą odwrotnej dystrybuanty: pierwsza kolumna,
        # w której dystrybuanta wiersza bieżącego stanu przekracza U.
        u = rng.random((m, n, 1))
        current = (u > cum_P[current]).sum(axis=2)
        states[t] = current
    return states


def generate_scenarios(
    S0=DEFAULT_S0,
    transition_matrix=DEFAULT_TRANSITION_MATRIX,
    initial_states=DEFAULT_INITIAL_STATES,
    mu=DEFAULT_MU,
    sigma=DEFAULT_SIGMA,
    T=20,
    m=1000,
    seed=42,
):
    """Generuje m scenariuszy cen n akcji w momencie T metodą Monte Carlo.

    Zwraca (s, p): s to tablica (m, n) cen w momencie T, p to wektor (m,)
    prawdopodobieństw scenariuszy, p_j = 1/m.
    """
    S0 = np.asarray(S0, dtype=float)
    initial_states = np.asarray(initial_states, dtype=np.int64)
    mu = np.asarray(mu, dtype=float)
    sigma = np.asarray(sigma, dtype=float)
    P = np.asarray(transition_matrix, dtype=float)

    _validate_transition_matrix(P)
    k = P.shape[0]
    if S0.shape != initial_states.shape:
        raise ValueError("S0 i initial_states muszą mieć ten sam rozmiar n.")
    if mu.shape != (k,) or sigma.shape != (k,):
        raise ValueError("mu i sigma muszą mieć po jednym elemencie na stan.")
    if np.any(initial_states < 0) or np.any(initial_states >= k):
        raise ValueError("Stany początkowe muszą być indeksami z zakresu [0, k).")

    rng = np.random.default_rng(seed)
    n = len(S0)

    states = _simulate_markov_states(P, initial_states, T, m, rng)

    Z = rng.standard_normal((T, m, n))
    returns = mu[states] + sigma[states] * Z
    s = S0 * np.prod(1.0 + returns, axis=0)

    p = np.full(m, 1.0 / m)
    return s, p


if __name__ == "__main__":
    s, p = generate_scenarios(T=20, m=1000)

    print(f"Liczba scenariuszy m = {s.shape[0]}, liczba akcji n = {s.shape[1]}")
    print(f"Suma prawdopodobieństw: {p.sum():.6f} (p_j = {p[0]:.4f})")
    print(f"\nCeny początkowe S0:      {DEFAULT_S0}")
    print(f"Średnie ceny w T:        {s.mean(axis=0).round(2)}")
    print(f"Odchylenie std cen w T:  {s.std(axis=0).round(2)}")
    print(f"Minimalne ceny w T:      {s.min(axis=0).round(2)}")
    print(f"Maksymalne ceny w T:     {s.max(axis=0).round(2)}")
    print(f"\nPrzykładowy scenariusz s_0: {s[0].round(2)}")
