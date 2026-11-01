"""Splitsort — заготовка, реализация предстоит.

Идея алгоритма: адаптивная сортировка Лефкопулоса и Петерссона. «Адаптивная»
означает, что время работы зависит не только от числа элементов n, но и от
предварительной отсортированности входа: чем ближе вход к отсортированному,
тем быстрее работает алгоритм. Splitsort разбивает вход на восходящие
подпоследовательности и постепенно объединяет их, достигая оптимальности
относительно числа инверсий (пар элементов, стоящих в неправильном порядке).

Ссылки на статьи в каталоге papers/:
- splitsort/Splitsort_an adaptive sorting algorithm-Levcopoulos-Petersson-1991.pdf
  — оригинальная статья с описанием алгоритма и доказательством оценок;
- adaptive_heapsort/Adaptive_Heapsort-Levcopoulos-Petersson-1993.pdf
  — родственная работа тех же авторов, полезна для сравнения подходов.
"""

from __future__ import annotations

from typing import Any, MutableSequence

from sorting_lab.base import Algorithm, AlgorithmInfo, Comparator, default_compare


class Splitsort(Algorithm):
    """Адаптивная сортировка Splitsort (Levcopoulos, Petersson, 1991).

    План реализации (по оригинальной статье):
    1. Разбиение входа на максимальные восходящие подпоследовательности.
    2. Многофазное слияние подпоследовательностей с учётом их длин.
    3. Согласовать реализацию с измерением числа инверсий входа
       (метрика адаптивности, см. ``sorting_lab.bench``) — на ней будет
       проверяться теоретическая оценка вида O(n log(Inv/n)).
    """

    def __init__(self) -> None:
        #: Паспорт алгоритма: формальные сведения из статьи-источника.
        self.info = AlgorithmInfo(
            name="splitsort",
            full_name="Splitsort: an adaptive sorting algorithm",
            reference="C. Levcopoulos, O. Petersson, 'Splitsort — an adaptive "
            "sorting algorithm', Information Processing Letters, 1991; "
            "papers/splitsort/",
            time_complexity="O(n log(Inv/n)) — зависит от числа инверсий Inv",
            space_complexity="O(n)",
            stable=False,
            in_place=False,
            notes="Реализация запланирована; модуль оформлен как заготовка.",
        )

    def sort(self, data: MutableSequence[Any], compare: Comparator = default_compare) -> None:
        """Отсортировать ``data``; полное описание контракта — в ``base.Algorithm.sort``."""
        raise NotImplementedError(
            "Splitsort ещё не реализован; см. план в docstring класса "
            "и статьи из papers/splitsort/."
        )
