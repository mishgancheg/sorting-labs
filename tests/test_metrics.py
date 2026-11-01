"""Тесты измерительного стенда: подсчёт сравнений и сбор метрик прогона."""

from __future__ import annotations

import pytest

from sorting_lab.bench.metrics import CountingComparator, measure
from sorting_lab.registry import get_algorithm, implemented_algorithms

IMPLEMENTED = implemented_algorithms()

if not IMPLEMENTED:
    pytest.skip("Ни один алгоритм ещё не реализован", allow_module_level=True)


def test_counting_comparator_counts_calls() -> None:
    """Обёртка считает каждый вызов и не искажает результат сравнения."""
    comparator = CountingComparator()
    assert comparator(1, 2) == -1
    assert comparator(2, 1) == 1
    assert comparator(5, 5) == 0
    assert comparator.comparisons == 3


@pytest.mark.parametrize("algorithm", IMPLEMENTED, ids=[a.info.name for a in IMPLEMENTED])
def test_measure_collects_metrics(algorithm) -> None:
    """Прогон возвращает метрики: сравнения посчитаны, результат корректен."""
    data = list(range(100, 0, -1))
    result = measure(algorithm, data, dataset_name="тест")
    assert result.correct
    assert result.comparisons > 0
    assert result.size == 100
    assert result.algorithm == algorithm.info.name
    # Исходные данные не изменяются — их можно использовать в новых прогонах.
    assert data == list(range(100, 0, -1))


def test_heap_sorter_registered_once() -> None:
    """Обращение по имени работает; пример: heapsort доступен в реестре."""
    algorithm = get_algorithm("heapsort")
    assert algorithm.info.name == "heapsort"
