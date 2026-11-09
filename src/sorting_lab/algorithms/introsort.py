"""Introsort (интроспективная сортировка) по статье Дэвида Массера (1997).

Идея алгоритма: начинается как быстрая сортировка (quicksort), но следит за
глубиной рекурсии. Как только глубина превышает 2 * floor(log2(n)) — признак
неудачного выбора опорных элементов и опасности худшего случая O(n^2), —
алгоритм переключается на пирамидальную сортировку, гарантирующую O(n log n).
Мелкие подмассивы (не длиннее 16 элементов) быстрая сортировка не трогает:
их дорабатывает один общий проход сортировки вставками в самом конце.
Так алгоритм «интроспектирует» (наблюдает за самим собой) и сохраняет
скорость быстрой сортировки в среднем случае, не имея её слабого худшего случая.

Реализация повторяет псевдокод INTROSORT / INTROSORT_LOOP из статьи Массера:
опорный элемент — медиана трёх (первого, среднего и последнего элемента),
разбиение — схема Хоара, рекурсия только по правой части, а левая часть
обрабатывается в том же цикле (это экономит глубину стека).

Ссылки на статьи в каталоге papers/:
- Introsort-introspecting_sort/Introspective_Sorting_and_Selection_Algorithms-Musser-1997.pdf
  — оригинальная статья Дэвида Массера, автора алгоритма;
- Introsort-introspecting_sort/Introspective_sorting_and_selection_revisited-Valois-2000.pdf
  — критика и уточнение оценок;
- Introsort-introspecting_sort/Efficient Verified Implementation of Introsort and Pdqsort-Lammich-2020.pdf
  — формально верифицированная реализация (с её псевдокодом удобно сверяться).
"""

from __future__ import annotations

from typing import Any, MutableSequence

from sorting_lab.algorithms.heapsort import Heapsort
from sorting_lab.base import Algorithm, AlgorithmInfo, Comparator, default_compare

#: Порог размера подмассива, ниже которого быстрая сортировка останавливается
#: и оставляет участок финальной сортировке вставками (значение из статьи Массера).
SIZE_THRESHOLD = 16


class Introsort(Algorithm):
    """Интроспективная сортировка: quicksort с контролем глубины рекурсии.

    Схема работы (по Musser, 1997):
    1. Быстрая сортировка с лимитом глубины ``2 * floor(log2(n))``.
    2. При исчерпании лимита — пирамидальная сортировка подмассива
       (используется готовый :class:`Heapsort` как строительный блок).
    3. Финальный проход сортировкой вставками по всему массиву
       (она дорабатывает короткие неотсортированные участки).
    """

    def __init__(self) -> None:
        #: Паспорт алгоритма: формальные сведения из статьи-источника.
        self.info = AlgorithmInfo(
            name="introsort",
            full_name="Introsort (introspective sort)",
            reference="D. R. Musser, 'Introspective Sorting and Selection "
            "Algorithms', Software: Practice and Experience, 1997; "
            "papers/Introsort-introspecting_sort/",
            time_complexity="O(n log n) в худшем случае",
            space_complexity="O(log n) — глубина рекурсии ограничена",
            stable=False,
            in_place=True,
            notes="Медиана трёх, разбиение Хоара, порог 16 элементов и "
            "отложенная сортировка вставками — как в псевдокоде Массера.",
        )
        self._heapsort = Heapsort()

    def sort(self, data: MutableSequence[Any], compare: Comparator = default_compare) -> None:
        """Отсортировать ``data``; полное описание контракта — в ``base.Algorithm.sort``."""
        n = len(data)
        if n < 2:
            return
        # Лимит глубины 2 * floor(log2(n)); bit_length() - 1 и есть floor(log2(n)).
        depth_limit = 2 * (n.bit_length() - 1)
        self._introsort_loop(data, 0, n, depth_limit, compare)
        # Быстрая сортировка оставила неупорядоченными только короткие участки
        # длиной не больше SIZE_THRESHOLD, причём каждый элемент уже лежит в
        # «своём» участке. Поэтому сортировка вставками сдвигает каждый элемент
        # не дальше чем на 16 позиций и работает за линейное время.
        self._insertion_sort(data, 0, n, compare)

    def _introsort_loop(
        self,
        data: MutableSequence[Any],
        lo: int,
        hi: int,
        depth_limit: int,
        compare: Comparator,
    ) -> None:
        """Быстрая сортировка участка ``data[lo:hi]`` с ограничением глубины.

        Аргументы:
            data: сортируемый массив;
            lo, hi: границы участка (``hi`` не включается);
            depth_limit: сколько ещё уровней разбиения разрешено, прежде чем
                перейти на пирамидальную сортировку;
            compare: компаратор сравнения элементов.
        """
        while hi - lo > SIZE_THRESHOLD:
            if depth_limit == 0:
                # Разбиения идут слишком неудачно — пирамидальная сортировка
                # доводит участок до конца за гарантированные O(m log m).
                self._heapsort.sort_range(data, lo, hi, compare)
                return
            depth_limit -= 1
            pivot = self._median_of_three(
                data[lo], data[lo + (hi - lo) // 2], data[hi - 1], compare
            )
            cut = self._partition(data, lo, hi, pivot, compare)
            # Рекурсия по правой части, левая обрабатывается следующей
            # итерацией цикла (как в псевдокоде Массера).
            self._introsort_loop(data, cut, hi, depth_limit, compare)
            hi = cut

    @staticmethod
    def _median_of_three(a: Any, b: Any, c: Any, compare: Comparator) -> Any:
        """Вернуть средний по величине из трёх элементов (медиану трёх)."""
        if compare(a, b) < 0:
            if compare(b, c) < 0:
                return b  # a < b < c
            if compare(a, c) < 0:
                return c  # a < c <= b
            return a  # c <= a < b
        if compare(a, c) < 0:
            return a  # b <= a < c
        if compare(b, c) < 0:
            return c  # b < c <= a
        return b  # c <= b <= a

    @staticmethod
    def _partition(
        data: MutableSequence[Any],
        lo: int,
        hi: int,
        pivot: Any,
        compare: Comparator,
    ) -> int:
        """Разбиение Хоара участка ``data[lo:hi]`` относительно значения ``pivot``.

        После разбиения все элементы левее возвращаемой границы не больше
        ``pivot``, а все элементы начиная с неё — не меньше ``pivot``.

        Внутренние циклы не проверяют выход за границы участка: это
        безопасно, потому что ``pivot`` — медиана трёх элементов самого
        участка, и первый указатель гарантированно остановится на элементе
        не меньше опорного, а второй — на элементе не больше опорного.
        Обе части разбиения получаются непустыми, поэтому алгоритм не
        зацикливается.
        """
        left, right = lo, hi
        while True:
            while compare(data[left], pivot) < 0:
                left += 1
            right -= 1
            while compare(pivot, data[right]) < 0:
                right -= 1
            if left >= right:
                return left
            data[left], data[right] = data[right], data[left]
            left += 1

    @staticmethod
    def _insertion_sort(
        data: MutableSequence[Any],
        lo: int,
        hi: int,
        compare: Comparator,
    ) -> None:
        """Сортировка вставками участка ``data[lo:hi]``.

        Каждый очередной элемент сдвигается влево, пока слева стоит
        строго больший элемент.
        """
        for i in range(lo + 1, hi):
            value = data[i]
            j = i - 1
            while j >= lo and compare(value, data[j]) < 0:
                data[j + 1] = data[j]
                j -= 1
            data[j + 1] = value
