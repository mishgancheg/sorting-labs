"""Тесты корректности алгоритмов из реестра.

Главная проверка: каждый реализованный алгоритм должен превращать любой
эталонный вход в правильно отсортированный массив (эталон — встроенная
функция sorted стандартной библиотеки). Тесты автоматически охватывают
новые алгоритмы: как только реализация перестаёт бросать
NotImplementedError, она попадает в проверку (см. registry.implemented_algorithms).
"""

from __future__ import annotations

import pytest

from sorting_lab.base import default_compare
from sorting_lab.datasets.edge_cases import EDGE_CASES
from sorting_lab.registry import implemented_algorithms

# Все реализованные на текущий момент алгоритмы; заготовки пропускаются.
IMPLEMENTED = implemented_algorithms()

if not IMPLEMENTED:
    pytest.skip("Ни один алгоритм ещё не реализован", allow_module_level=True)


@pytest.mark.parametrize("case_name,case_data", EDGE_CASES, ids=[name for name, _ in EDGE_CASES])
@pytest.mark.parametrize("algorithm", IMPLEMENTED, ids=[a.info.name for a in IMPLEMENTED])
def test_sorts_edge_cases_correctly(algorithm, case_name: str, case_data: list) -> None:
    """Алгоритм сортирует крайний случай так же, как эталонная sorted()."""
    data = list(case_data)
    algorithm.sort(data)
    assert data == sorted(case_data)


@pytest.mark.parametrize(
    "generator_name",
    ["random_uniform", "nearly_sorted", "few_unique", "sawtooth"],
)
@pytest.mark.parametrize("algorithm", IMPLEMENTED, ids=[a.info.name for a in IMPLEMENTED])
def test_sorts_generated_data(algorithm, generator_name: str) -> None:
    """Алгоритм сортирует случайные входы умеренного размера."""
    from sorting_lab.datasets.generators import GENERATORS

    data = GENERATORS[generator_name](n=500, seed=12345)
    algorithm.sort(data)
    assert data == sorted(data)


@pytest.mark.parametrize("algorithm", IMPLEMENTED, ids=[a.info.name for a in IMPLEMENTED])
def test_custom_comparator_is_used(algorithm) -> None:
    """Алгоритм уважает переданный компаратор: сортирует по убыванию при обратном сравнении.

    Компаратор, возвращающий противоположный знак, меняет порядок на убывающий.
    Это проверяет контракт: сравнение идёт только через компаратор
    (иначе подсчёт сравнений в измерительном стенде был бы невозможен).
    """
    data = [3, 1, 4, 1, 5, 9, 2, 6]
    descending_compare = lambda a, b: -default_compare(a, b)  # noqa: E731
    algorithm.sort(data, descending_compare)
    assert data == sorted(data, reverse=True)


@pytest.mark.parametrize("algorithm", IMPLEMENTED, ids=[a.info.name for a in IMPLEMENTED])
def test_sorts_random_inputs_of_many_sizes(algorithm) -> None:
    """Алгоритм сортирует случайные массивы всех размеров от 0 до 120.

    Перебор размеров ловит ошибки на границах: порог переключения на
    сортировку вставками в Introsort, минимальная длина run'а в Powersort,
    нечётные длины в рекурсии Splitsort и тому подобное.
    """
    import random

    rng = random.Random(2026)
    for size in range(121):
        for value_range in (3, 1000):
            data = [rng.randrange(value_range) for _ in range(size)]
            expected = sorted(data)
            algorithm.sort(data)
            assert data == expected, f"размер {size}, диапазон значений {value_range}"


STABLE = [a for a in IMPLEMENTED if a.info.stable]


@pytest.mark.parametrize("algorithm", STABLE, ids=[a.info.name for a in STABLE])
def test_stable_algorithms_keep_order_of_equal_keys(algorithm) -> None:
    """Устойчивый алгоритм (stable=True в паспорте) не переставляет равные элементы.

    Элементы — пары (ключ, исходная позиция), а компаратор смотрит только
    на ключ. Если алгоритм устойчив, при равных ключах позиции остаются
    в возрастающем порядке, то есть результат совпадает с sorted() по парам.
    """
    import random

    rng = random.Random(7)
    keys = [rng.randrange(10) for _ in range(500)]
    data = [(key, position) for position, key in enumerate(keys)]
    by_key = lambda a, b: default_compare(a[0], b[0])  # noqa: E731
    algorithm.sort(data, by_key)
    assert data == sorted(data)


ADAPTIVE = [a for a in IMPLEMENTED if a.info.name in {"powersort", "splitsort", "adaptive_heapsort"}]


@pytest.mark.parametrize("algorithm", ADAPTIVE, ids=[a.info.name for a in ADAPTIVE])
def test_adaptive_algorithms_are_linear_on_sorted_input(algorithm) -> None:
    """Адаптивный алгоритм на уже отсортированном входе делает O(n) сравнений.

    Статьи-источники обещают линейное число сравнений на отсортированном
    входе; проверяем с запасом, что их меньше 2n (обычный heapsort
    на таком входе тратит около 2 n log2 n, то есть в десятки раз больше).
    """
    from sorting_lab.bench.metrics import CountingComparator

    n = 2000
    data = list(range(n))
    comparator = CountingComparator()
    algorithm.sort(data, comparator)
    assert data == list(range(n))
    assert comparator.comparisons < 2 * n
