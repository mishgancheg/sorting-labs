"""Тесты генераторов данных и подсчёта инверсий.

Проверяются два ключевых свойства генераторов: воспроизводимость (одно
зерно — один массив) и размер. Для подсчёта инверсий проверяются известные
значения на маленьких входах и сравнение с наивным перебором пар.
"""

from __future__ import annotations

import random

import pytest

from sorting_lab.bench.metrics import count_inversions
from sorting_lab.datasets.generators import GENERATORS


@pytest.mark.parametrize("generator_name", sorted(GENERATORS))
def test_generator_size_matches_request(generator_name: str) -> None:
    """Генератор возвращает ровно столько элементов, сколько запрошено."""
    assert len(GENERATORS[generator_name](n=100, seed=1)) == 100


@pytest.mark.parametrize("generator_name", sorted(GENERATORS))
def test_generator_is_reproducible(generator_name: str) -> None:
    """Одно и то же зерно даёт одинаковый массив; другое зерно — другой."""
    first = GENERATORS[generator_name](n=100, seed=42)
    second = GENERATORS[generator_name](n=100, seed=42)
    assert first == second


@pytest.mark.parametrize("generator_name", ["random_uniform", "nearly_sorted", "few_unique"])
def test_different_seeds_give_different_data(generator_name: str) -> None:
    """Разные зёрна дают разные массивы (иначе «случайность» сломана)."""
    first = GENERATORS[generator_name](n=100, seed=0)
    second = GENERATORS[generator_name](n=100, seed=1)
    assert first != second


def test_nearly_sorted_has_few_inversions() -> None:
    """Почти отсортированный вход действительно близок к отсортированному.

    При малой доле сбоев (5%) число инверсий должно быть значительно меньше
    максимума n(n-1)/2 для случайного массива того же размера.
    """
    from sorting_lab.datasets.generators import nearly_sorted

    data = nearly_sorted(n=1000, seed=7, disorder=0.05)
    max_inversions = 1000 * 999 // 2
    assert count_inversions(data) < max_inversions / 100


def test_sorted_cases_inversions() -> None:
    """Известные значения инверсий: отсортирован — 0, обратно отсортирован — максимум."""
    from sorting_lab.datasets.generators import sorted_ascending, sorted_descending

    n = 10
    assert count_inversions(sorted_ascending(n)) == 0
    assert count_inversions(sorted_descending(n)) == n * (n - 1) // 2


def test_inversions_matches_naive_count() -> None:
    """Быстрый подсчёт инверсий совпадает с прямым перебором всех пар."""
    rng = random.Random(0)
    data = [rng.randrange(50) for _ in range(200)]
    naive = sum(
        1
        for i in range(len(data))
        for j in range(i + 1, len(data))
        if data[i] > data[j]
    )
    assert count_inversions(data) == naive
