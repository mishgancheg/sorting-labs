"""Пирамидальная сортировка (heapsort) — образец стиля для всех алгоритмов проекта.

Этот модуль служит эталоном оформления: по такому шаблону оформляются
остальные сортировки (шапка со ссылкой на статью, паспорт алгоритма,
подробные комментарии к неочевидным шагам).

Идея алгоритма: массив сначала перестраивается в двоичную кучу (пирамиду) —
структуру, где каждый родитель не меньше своих детей, — затем максимум
(корень кучи) многократно меняется местами с последним неотсортированным
элементом, и куча восстанавливается просеиванием вниз. Так на каждом шаге
из необработанной части извлекается наибольший элемент.

Помимо сортировки всего массива модуль умеет сортировать участок
``data[lo:hi]`` на месте (метод :meth:`Heapsort.sort_range`): этим пользуется
Introsort, переключаясь на пирамидальную сортировку для отдельного подмассива.

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
            notes="Строительный блок для Introsort (сортировка подмассива "
            "при исчерпании лимита глубины рекурсии).",
        )

    def sort(self, data: MutableSequence[Any], compare: Comparator = default_compare) -> None:
        """Отсортировать ``data`` по неубыванию, строим кучу и извлекаем максимумы.

        Полное описание контракта аргументов см. в ``sorting_lab.base.Algorithm.sort``.
        """
        self.sort_range(data, 0, len(data), compare)

    def sort_range(
        self,
        data: MutableSequence[Any],
        lo: int,
        hi: int,
        compare: Comparator = default_compare,
    ) -> None:
        """Отсортировать на месте участок ``data[lo:hi]``, не трогая остальное.

        Куча строится прямо внутри участка: элемент с индексом ``lo`` играет
        роль корня, а все индексы кучи отсчитываются от ``lo``.
        """
        n = hi - lo
        if n < 2:
            # Участок из нуля или одного элемента уже отсортирован.
            return

        # Этап 1. Построение кучи. Идём от последнего родителя к корню и
        # просеиваем каждого родителя вниз; после прохода весь участок — куча.
        # Родитель узла с номером i находится по формуле (i - 1) // 2,
        # поэтому последний родитель имеет номер n // 2 - 1.
        for start in range(n // 2 - 1, -1, -1):
            self._sift_down(data, lo, start, n, compare)

        # Этап 2. Разбор кучи. Корень — наибольший элемент неотсортированной
        # части; меняем его с последним элементом этой части, уменьшаем
        # границу кучи на единицу и восстанавливаем свойство кучи просеиванием.
        for end in range(n - 1, 0, -1):
            data[lo], data[lo + end] = data[lo + end], data[lo]
            self._sift_down(data, lo, 0, end, compare)

    @staticmethod
    def _sift_down(
        data: MutableSequence[Any],
        offset: int,
        root: int,
        size: int,
        compare: Comparator,
    ) -> None:
        """Просеивание вниз: опустить узел ``root`` до его законного места.

        Узел меняется местами с наибольшим из своих детей до тех пор, пока
        оба ребёнка не окажутся не больше него. Рассматриваются только узлы
        с номерами меньше ``size`` — правее этой границы куча уже разобрана
        и элементы стоят на финальных местах.

        Аргументы:
            data: массив, внутри которого лежит куча;
            offset: индекс в ``data``, с которого начинается куча (её корень);
                узел с номером i хранится в ``data[offset + i]``;
            root: номер узла, с которого начинается просеивание;
            size: текущий размер кучи (граница неотсортированной части);
            compare: компаратор сравнения элементов.
        """
        while True:
            # Номера детей узла root в двоичной куче, хранимой в массиве.
            left = 2 * root + 1
            right = 2 * root + 2
            largest = root

            # Ищем наибольший среди узла и его детей. Положительное значение
            # compare(a, b) означает, что a больше b.
            if left < size and compare(data[offset + left], data[offset + largest]) > 0:
                largest = left
            if right < size and compare(data[offset + right], data[offset + largest]) > 0:
                largest = right

            if largest == root:
                # Узел уже не меньше своих детей — свойство кучи восстановлено.
                return

            i, j = offset + root, offset + largest
            data[i], data[j] = data[j], data[i]
            # Продолжаем просеивание из позиции, куда переместили элемент.
            root = largest
