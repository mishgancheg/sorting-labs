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
