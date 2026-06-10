"""Moduł generowania scenariuszy rynkowych za pomocą łańcuchów Markova.

Model rynku typu "regime-switching": każda akcja w każdej chwili t znajduje
się w jednym ze stanów rynku (hossa / stagnacja / bessa). Stan ewoluuje
w czasie zgodnie z jednorodnym łańcuchem Markova o zadanej macierzy
przejścia, a bieżący stan determinuje rozkład jednookresowej stopy zwrotu:

    S_{t+1} = S_t * (1 + mu(stan) + sigma(stan) * Z),   Z ~ N(0, 1).

Symulacja Monte Carlo m niezależnych trajektorii na T kroków daje m
scenariuszy cen s_j w momencie T, każdy z prawdopodobieństwem p_j = 1/m.
Zwracane (s_j, p_j) są dokładnie w formacie wymaganym przez model
optymalizacyjny CVaR z PDF-a (skończona przestrzeń probabilistyczna).
"""

import numpy as np

# ---------------------------------------------------------------------------
# Definicja stanów rynku i parametrów modelu
# ---------------------------------------------------------------------------

#: Nazwy stanów rynku; indeks w krotce = numer stanu w łańcuchu Markova.
STATE_NAMES = ("hossa", "stagnacja", "bessa")

#: Macierz przejścia łańcucha Markova P[i, j] = P(stan_{t+1} = j | stan_t = i).
#: Stany rynku są trwałe (duże wartości na diagonali), a przejście
#: hossa <-> bessa z pominięciem stagnacji jest mało prawdopodobne.
DEFAULT_TRANSITION_MATRIX = np.array(
    [
        # hossa  stagnacja  bessa
        [0.80,   0.15,      0.05],   # z hossy
        [0.20,   0.60,      0.20],   # ze stagnacji
        [0.05,   0.25,      0.70],   # z bessy
    ]
)

#: Średnia jednookresowa stopa zwrotu w każdym stanie rynku.
DEFAULT_MU = np.array([0.008, 0.000, -0.010])

#: Odchylenie standardowe jednookresowej stopy zwrotu w każdym stanie
#: (bessa jest najbardziej zmienna).
DEFAULT_SIGMA = np.array([0.015, 0.010, 0.025])

#: Ceny początkowe S0 dla n = 5 akcji.
DEFAULT_S0 = np.array([100.0, 50.0, 75.0, 120.0, 90.0])

#: Stany początkowe akcji w chwili 0: dwie w hossie (0), dwie w stagnacji (1),
#: jedna w bessie (2).
DEFAULT_INITIAL_STATES = np.array([0, 0, 1, 1, 2])


# ---------------------------------------------------------------------------
# Funkcje pomocnicze
# ---------------------------------------------------------------------------

def _validate_transition_matrix(transition_matrix):
    """Sprawdza, czy macierz jest poprawną macierzą stochastyczną.

    Parameters
    ----------
    transition_matrix : np.ndarray
        Macierz kwadratowa (k, k) z nieujemnymi wierszami sumującymi się do 1.

    Raises
    ------
    ValueError
        Gdy macierz nie jest kwadratowa, ma elementy ujemne lub wiersze
        nie sumują się do 1.
    """
    P = np.asarray(transition_matrix)
    if P.ndim != 2 or P.shape[0] != P.shape[1]:
        raise ValueError("Macierz przejścia musi być kwadratowa.")
    if np.any(P < 0):
        raise ValueError("Macierz przejścia nie może mieć elementów ujemnych.")
    if not np.allclose(P.sum(axis=1), 1.0):
        raise ValueError("Wiersze macierzy przejścia muszą sumować się do 1.")


def _simulate_markov_states(transition_matrix, initial_states, T, m, rng):
    """Symuluje trajektorie stanów łańcucha Markova dla wszystkich scenariuszy.

    Parameters
    ----------
    transition_matrix : np.ndarray
        Macierz przejścia (k, k) między stanami rynku.
    initial_states : np.ndarray
        Wektor (n,) stanów początkowych poszczególnych akcji.
    T : int
        Liczba kroków czasowych.
    m : int
        Liczba scenariuszy (niezależnych trajektorii).
    rng : np.random.Generator
        Generator liczb losowych.

    Returns
    -------
    np.ndarray
        Tablica (T, m, n) stanów rynku: states[t, j, i] to stan i-tej akcji
        w j-tym scenariuszu po t+1 krokach.
    """
    n = len(initial_states)
    cum_P = np.cumsum(transition_matrix, axis=1)

    states = np.empty((T, m, n), dtype=np.int64)
    current = np.broadcast_to(initial_states, (m, n)).copy()
    for t in range(T):
        # Próbkowanie kolejnego stanu metodą odwrotnej dystrybuanty:
        # losujemy U ~ U(0,1) i szukamy pierwszej kolumny, w której
        # dystrybuanta wiersza bieżącego stanu przekracza U.
        u = rng.random((m, n, 1))
        current = (u > cum_P[current]).sum(axis=2)
        states[t] = current
    return states


# ---------------------------------------------------------------------------
# Główna funkcja modułu
# ---------------------------------------------------------------------------

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
    """Generuje scenariusze cen akcji w momencie T metodą Monte Carlo.

    Każdy scenariusz to niezależna symulacja rynku na T kroków: stany rynku
    poszczególnych akcji ewoluują zgodnie z łańcuchem Markova, a ceny
    zmieniają się multiplikatywnie ze stopą zwrotu losowaną z rozkładu
    normalnego o parametrach zależnych od bieżącego stanu.

    Parameters
    ----------
    S0 : np.ndarray
        Wektor (n,) cen początkowych akcji.
    transition_matrix : np.ndarray
        Macierz przejścia (k, k) między stanami rynku.
    initial_states : np.ndarray
        Wektor (n,) stanów początkowych akcji (indeksy w STATE_NAMES).
    mu : np.ndarray
        Wektor (k,) średnich stóp zwrotu w poszczególnych stanach.
    sigma : np.ndarray
        Wektor (k,) odchyleń standardowych stóp zwrotu w stanach.
    T : int
        Horyzont symulacji (liczba kroków czasowych).
    m : int
        Liczba scenariuszy do wygenerowania.
    seed : int or None
        Ziarno generatora losowego (None = losowe ziarno).

    Returns
    -------
    s : np.ndarray
        Tablica (m, n) cen akcji w momencie T; s[j] to wektor cen s_j
        w j-tym scenariuszu.
    p : np.ndarray
        Wektor (m,) prawdopodobieństw scenariuszy, p_j = 1/m.

    Raises
    ------
    ValueError
        Gdy wymiary danych wejściowych są niespójne lub macierz przejścia
        nie jest stochastyczna.
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

    # Trajektorie stanów rynku: (T, m, n).
    states = _simulate_markov_states(P, initial_states, T, m, rng)

    # Stopy zwrotu zależne od stanu i multiplikatywna ewolucja cen.
    Z = rng.standard_normal((T, m, n))
    returns = mu[states] + sigma[states] * Z
    s = S0 * np.prod(1.0 + returns, axis=0)

    p = np.full(m, 1.0 / m)
    return s, p


# ---------------------------------------------------------------------------
# Demonstracja działania modułu
# ---------------------------------------------------------------------------

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
