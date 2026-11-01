"""Метрики измерительного стенда.

Сейчас реализованы базовые метрики, достаточные для сравнения алгоритмов
по теории из статей:

- число сравнений — считается точно: компаратор-обёртка
  :class:`CountingComparator` передаётся алгоритму и считает каждый вызов;
- число перемещений — не реализовано, добавляется, когда будет ясно, какие
  именно операции считать перемещением для каждого алгоритма;
- время выполнения — вспомогательная метрика (зависит от машины).

Архитектура расширяемая: новые метрики добавляются как новые поля
:class:`RunMetrics` и шаги в :func:`measure` без изменения алгоритмов.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Callable, MutableSequence

from sorting_lab.base import Algorithm, Comparator, default_compare


class CountingComparator:
    """Обёртка над компаратором, подсчитывающая число вызовов сравнения.

    Алгоритм получает этот объект как обычную функцию двух аргументов
    (он вызывается так же, как ``compare(a, b)``), поэтому сам код
    алгоритма никак не меняется. Число вызовов после прогона лежит
    в атрибуте ``comparisons``.

    Аргументы:
        inner: настоящий компаратор, например ``default_compare``.
    """

    def __init__(self, inner: Comparator = default_compare) -> None:
        self._inner = inner
        #: Число выполненных сравнений за всё время жизни объекта.
        self.comparisons: int = 0

    def __call__(self, first: Any, second: Any) -> int:
        self.comparisons += 1
        return self._inner(first, second)


@dataclass(frozen=True)
class RunMetrics:
    """Результаты одного прогона алгоритма на одном наборе данных.

    Атрибуты:
        algorithm: имя алгоритма из реестра;
        dataset: название набора данных (имя генератора или крайнего случая);
        size: число элементов входа;
        comparisons: число сравнений элементов за прогон;
        elapsed_seconds: время выполнения (вспомогательная метрика,
            зависит от машины и версии интерпретатора);
        correct: прошла ли проверка — совпал ли результат с эталонным
            ``sorted()`` из стандартной библиотеки.
    """

    algorithm: str
    dataset: str
    size: int
    comparisons: int
    elapsed_seconds: float
    correct: bool


def measure(
    algorithm: Algorithm,
    data: MutableSequence[Any],
    dataset_name: str = "",
) -> RunMetrics:
    """Прогнать алгоритм на копии данных и собрать метрики прогона.

    Аргументы:
        algorithm: объект алгоритма из реестра;
        data: входная последовательность; сортируется копия, поэтому
            переданные данные не изменяются и их можно использовать
            в нескольких прогонах;
        dataset_name: человекочитаемое название набора данных для отчёта.

    Возвращает :class:`RunMetrics` с числом сравнений, временем и признаком
    корректности результата.
    """
    working_copy = list(data)
    comparator = CountingComparator()

    start = time.perf_counter_ns()
    algorithm.sort(working_copy, comparator)
    elapsed = (time.perf_counter_ns() - start) / 1e9

    return RunMetrics(
        algorithm=algorithm.info.name,
        dataset=dataset_name,
        size=len(data),
        comparisons=comparator.comparisons,
        elapsed_seconds=elapsed,
        correct=working_copy == sorted(data),
    )


def count_inversions(data: MutableSequence[Any]) -> int:
    """Подсчитать число инверсий входа: пар (i, j), где i < j, а data[i] > data[j].

    Инверсия — стандартная мера предварительной отсортированности для
    адаптивных алгоритмов (Levcopoulos-Petersson): у отсортированного входа
    инверсий ноль, у обратно отсортированного — n(n-1)/2. Подсчёт выполнен
    слиянием за O(n log n) — наивный перебор всех пар за O(n^2) на больших
    массивах работал бы слишком долго.
    """
    return _merge_count(list(data))[1]


def _merge_count(items: list[Any]) -> tuple[list[Any], int]:
    """Вспомогательная функция: сортировка слиянием с подсчётом инверсий.

    Возвращает пару (отсортированная копия, число инверсий внутри ``items``).
    Идея: при слиянии двух половин, когда из правой половины берётся элемент
    раньше оставшихся левых, все оставшиеся левые образуют инверсии с ним.
    """
    if len(items) < 2:
        return items, 0
    middle = len(items) // 2
    left, inv_left = _merge_count(items[:middle])
    right, inv_right = _merge_count(items[middle:])
    merged: list[Any] = []
    inversions = inv_left + inv_right
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
            # Все оставшиеся элементы левой половины больше right[j] и стоят
            # в исходном массиве раньше — каждая такая пара есть инверсия.
            inversions += len(left) - i
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged, inversions
