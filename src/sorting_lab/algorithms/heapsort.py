"""Пирамидальная сортировка (heapsort) — образец стиля для всех алгоритмов проекта.

Этот модуль реализован полностью и служит эталоном оформления: по такому шаблону
оформляются остальные сортировки (шапка со ссылкой на статью, паспорт алгоритма,
подробные комментарии к неочевидным шагам).

Идея алгоритма: массив сначала перестраивается в двоичную кучу (пирамиду) —
структуру, где каждый родитель не меньше своих детей, — затем максимум
(корень кучи) многократно меняется местами с последним неотсортированным
элементом, и куча восстанавливается просеиванием вниз. Так на каждом шаге
из необработанной части извлекается наибольший элемент.

Ссылки на статьи в каталоге papers/:
- heapsort/Heapsort-Wikipedia.pdf — обзор и псевдокод;
- Wegner-Sorting__The_Turku_Lectures-2014.pdf — теоретический разбор.
"""

from __future__ import annotations

from typing import Any, MutableSequence

from sorting_lab.base import Algorithm, AlgorithmInfo, Comparator, default_compare


class Heapsort(Algorithm):
    """Классическая пирамидальная сортировка на месте."""

    def __init__(self) -> None:
        #: Паспорт алгоритма: формальные сведения из статьи-источника.
        self.info = AlgorithmInfo(
            name="heapsort",
            full_name="Heapsort (пирамидальная сортировка)",
            reference="J. W. J. Williams, 'Algorithm 232: Heapsort', 1964; "
            "обзор: papers/heapsort/Heapsort-Wikipedia.pdf",
            time_complexity="O(n log n) в худшем, среднем и лучшем случае",
            space_complexity="O(1) дополнительной памяти",
            stable=False,
            in_place=True,
            notes="Базовый строительный блок для Introsort и адаптивной "
            "пирамидальной сортировки (Levcopoulos-Petersson).",
        )

    def sort(self, data: MutableSequence[Any], compare: Comparator = default_compare) -> None:
        """Отсортировать ``data`` по неубыванию, строим кучу и извлекаем максимумы.

        Полное описание контракта аргументов см. в ``sorting_lab.base.Algorithm.sort``.
        """
        n = len(data)
        if n < 2:
            # Последовательности из нуля или одного элемента уже отсортированы.
            return

        # Этап 1. Построение кучи. Идём от последнего родителя к корню и
        # просеиваем каждого родителя вниз; после прохода весь массив — куча.
        # Родитель узла с индексом i находится по формуле (i - 1) // 2,
        # поэтому последний родитель имеет индекс n // 2 - 1.
        for start in range(n // 2 - 1, -1, -1):
            self._sift_down(data, start, n, compare)

        # Этап 2. Разбор кучи. Корень — наибольший элемент неотсортированной
        # части; меняем его с последним элементом этой части, уменьшаем
        # границу кучи на единицу и восстанавливаем свойство кучи просеиванием.
        for end in range(n - 1, 0, -1):
            data[0], data[end] = data[end], data[0]
            self._sift_down(data, 0, end, compare)

    @staticmethod
    def _sift_down(
        data: MutableSequence[Any],
        root: int,
        size: int,
        compare: Comparator,
    ) -> None:
        """Просеивание вниз: опустить узел ``root`` до его законного места.

        Узел меняется местами с наибольшим из своих детей до тех пор, пока
        оба ребёнка не окажутся не больше него. Рассматриваются только узлы
        с индексами меньше ``size`` — правее этой границы куча уже разобрана
        и элементы стоят на финальных местах.

        Аргументы:
            data: массив, первые ``size`` элементов которого образуют кучу;
            root: индекс узла, с которого начинается просеивание;
            size: текущий размер кучи (граница неотсортированной части);
            compare: компаратор сравнения элементов.
        """
        while True:
            # Индексы детей узла root в двоичной куче, хранимой в массиве.
            left = 2 * root + 1
            right = 2 * root + 2
            largest = root

            # Ищем наибольший среди узла и его детей. Отрицательное значение
            # compare(a, b) означает, что a меньше b.
            if left < size and compare(data[left], data[largest]) > 0:
                largest = left
            if right < size and compare(data[right], data[largest]) > 0:
                largest = right

            if largest == root:
                # Узел уже не меньше своих детей — свойство кучи восстановлено.
                return

            data[root], data[largest] = data[largest], data[root]
            # Продолжаем просеивание из позиции, куда переместили элемент.
            root = largest
