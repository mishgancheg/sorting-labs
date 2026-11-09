"""Powersort — устойчивая сортировка слиянием естественных run'ов (Munro, Wild).

Идея алгоритма: улучшение TimSort-подобной схемы. Вход разбивается на
естественные упорядоченные подпоследовательности — run'ы (неубывающие
берутся как есть, строго убывающие разворачиваются). Run'ы по очереди
кладутся на стек, и решение, когда сливать, принимается по «степени»
(power) границы между соседними run'ами.

Степень границы определяется так. Каждый run представляется отрезком
внутри [0, 1] (позиция и длина делятся на n), и берутся середины двух
соседних run'ов. Степень — это наименьшее k, при котором середины
попадают в разные отрезки разбиения [0, 1] на 2^k равных частей. Чем
меньше степень, тем «выше» эта граница в почти оптимальном дереве
слияний. Правило: пока у верхнего элемента стека степень больше степени
новой границы, верхний run сливается с текущим. В результате дерево
слияний близко к оптимальному (стоимость не более H + 2 на элемент, где
H — энтропия распределения длин run'ов), а стек имеет глубину O(log n).

Как в TimSort и авторских реализациях, короткие run'ы искусственно
удлиняются до ``MIN_RUN_LEN`` элементов сортировкой вставками — на
очень коротких участках она дешевле слияний.

Реализован классический двухпутевой Powersort (k = 2 в определении 3.1
статьи о Multiway Powersort); именно этот вариант используется в CPython
начиная с версии 3.11.

Ссылки на статьи в каталоге papers/:
- powersort/Multiway_Powersort-Cawley_Gelling-Nebel-Smith-Wild-2023.pdf
  — статья о многопутевом (multiway) варианте Powersort, включая
  определение степени границы run'ов и обзор классического алгоритма;
- powersort/sebawild_powersort_Cpp_implementations_of_Powersort_and_4_way_Powersort.pdf
  — авторские реализации на C++ (Sebastian Wild), по ним сверялся главный цикл.
"""

from __future__ import annotations

from typing import Any, MutableSequence

from sorting_lab.base import Algorithm, AlgorithmInfo, Comparator, default_compare

#: Минимальная длина run'а: более короткие run'ы дополняются сортировкой вставками.
MIN_RUN_LEN = 16


class Powersort(Algorithm):
    """Сортировка слиянием с выбором слияний по степени границы run'ов.

    Схема работы:
    1. Разбиение входа на естественные run'ы; строго убывающие
       разворачиваются на месте, короткие удлиняются до ``MIN_RUN_LEN``.
    2. Для каждой новой границы вычисляется степень; пока степень на
       вершине стека больше, верхний run сливается с текущим.
    3. В конце все оставшиеся на стеке run'ы сливаются сверху вниз.
       Слияние устойчиво — равные элементы сохраняют исходный порядок.
    """

    def __init__(self) -> None:
        #: Паспорт алгоритма: формальные сведения из статьи-источника.
        self.info = AlgorithmInfo(
            name="powersort",
            full_name="Powersort",
            reference="J. I. Munro, S. Wild, 'Nearly-Optimal Mergesorts', "
            "ESA 2018; W. Cawley Gelling, M. E. Nebel, B. Smith, S. Wild, "
            "'Multiway Powersort', ALENEX 2023; papers/powersort/",
            time_complexity="O(n log n) в худшем случае, O(n + n H) с учётом "
            "run'ов (H — энтропия длин run'ов)",
            space_complexity="O(n) — буфер для слияния",
            stable=True,
            in_place=False,
            notes="Двухпутевой вариант (k = 2); MIN_RUN_LEN = 16, короткие "
            "run'ы удлиняются двоичными вставками.",
        )

    def sort(self, data: MutableSequence[Any], compare: Comparator = default_compare) -> None:
        """Отсортировать ``data``; полное описание контракта — в ``base.Algorithm.sort``."""
        n = len(data)
        if n < 2:
            return

        # Стек хранит пары (начало run'а, степень границы справа от него).
        # Конец run'а на стеке не нужен: он совпадает с началом следующего.
        # Нижний элемент со степенью 0 — сторож: степень любой реальной
        # границы не меньше 1, поэтому цикл слияний до него не дойдёт.
        stack: list[tuple[int, int]] = [(0, 0)]

        # Текущий run A = data[a_begin:a_end] ещё не положен на стек.
        a_begin = 0
        a_end = self._extend_run(data, a_begin, n, compare)
        while a_end < n:
            # Следующий run B = data[a_end:b_end].
            b_end = self._extend_run(data, a_end, n, compare)
            power = self._node_power(a_begin, a_end, b_end, n)
            # Инвариант: степени на стеке не убывают снизу вверх. Пока на
            # вершине степень больше новой, сливаем верхний run с run'ом A.
            while stack[-1][1] > power:
                top_begin, _ = stack.pop()
                self._merge(data, top_begin, a_begin, a_end, compare)
                a_begin = top_begin
            stack.append((a_begin, power))
            a_begin, a_end = a_end, b_end

        # Входные run'ы закончились: сливаем стек сверху вниз с последним run'ом.
        while len(stack) > 1:
            top_begin, _ = stack.pop()
            self._merge(data, top_begin, a_begin, a_end, compare)
            a_begin = top_begin

    @staticmethod
    def _node_power(begin_a: int, begin_b: int, end_b: int, n: int) -> int:
        """Степень границы между run'ами ``[begin_a, begin_b)`` и ``[begin_b, end_b)``.

        Чтобы обойтись целыми числами, берутся удвоенные середины run'ов
        ``a = begin_a + begin_b`` и ``b = begin_b + end_b``; их положение на
        отрезке [0, 1] равно a / (2n) и b / (2n). Цикл по очереди получает
        двоичные цифры этих дробей после запятой (сравнение с n равносильно
        вопросу «дробь не меньше 1/2?») и останавливается на первой цифре,
        где они различаются. Её номер и есть степень. Тот же приём применён
        в функции powerloop в CPython.
        """
        a = begin_a + begin_b
        b = begin_b + end_b
        power = 0
        while True:
            power += 1
            if a >= n:
                # Очередная двоичная цифра у обеих дробей равна 1 — отбрасываем её.
                a -= n
                b -= n
            elif b >= n:
                # У a цифра 0, у b — 1: середины разошлись на этом уровне.
                return power
            # Сдвиг на один двоичный разряд: переходим к следующей цифре.
            a <<= 1
            b <<= 1

    def _extend_run(
        self,
        data: MutableSequence[Any],
        begin: int,
        n: int,
        compare: Comparator,
    ) -> int:
        """Найти run, начинающийся с ``begin``, и вернуть его конец (не включая).

        Неубывающий run берётся как есть. Строго убывающий разворачивается
        на месте; строгость нужна для устойчивости: равные элементы внутри
        убывающего run'а поменяли бы порядок при развороте. Если run короче
        ``MIN_RUN_LEN``, он дополняется следующими элементами и сортируется
        двоичными вставками.
        """
        end = begin + 1
        if end < n:
            if compare(data[end], data[begin]) < 0:
                # Строго убывающий run.
                while end + 1 < n and compare(data[end + 1], data[end]) < 0:
                    end += 1
                end += 1
                self._reverse(data, begin, end)
            else:
                # Неубывающий run.
                while end + 1 < n and compare(data[end + 1], data[end]) >= 0:
                    end += 1
                end += 1

        if end - begin < MIN_RUN_LEN and end < n:
            sorted_end = end
            end = min(n, begin + MIN_RUN_LEN)
            self._binary_insertion_sort(data, begin, sorted_end, end, compare)
        return end

    @staticmethod
    def _reverse(data: MutableSequence[Any], lo: int, hi: int) -> None:
        """Развернуть участок ``data[lo:hi]`` на месте."""
        hi -= 1
        while lo < hi:
            data[lo], data[hi] = data[hi], data[lo]
            lo += 1
            hi -= 1

    @staticmethod
    def _binary_insertion_sort(
        data: MutableSequence[Any],
        lo: int,
        start: int,
        hi: int,
        compare: Comparator,
    ) -> None:
        """Досортировать ``data[lo:hi]`` вставками, если ``data[lo:start]`` уже отсортирован.

        Место вставки ищется двоичным поиском, что сокращает число
        сравнений до O(log m) на элемент. Новый элемент вставляется правее
        всех равных ему, поэтому сортировка устойчива.
        """
        for i in range(start, hi):
            value = data[i]
            left, right = lo, i
            while left < right:
                mid = (left + right) // 2
                if compare(value, data[mid]) < 0:
                    right = mid
                else:
                    left = mid + 1
            # Сдвигаем элементы data[left:i] на одну позицию вправо.
            for j in range(i, left, -1):
                data[j] = data[j - 1]
            data[left] = value

    @staticmethod
    def _merge(
        data: MutableSequence[Any],
        lo: int,
        mid: int,
        hi: int,
        compare: Comparator,
    ) -> None:
        """Устойчиво слить соседние отсортированные участки ``data[lo:mid]`` и ``data[mid:hi]``.

        Левый участок копируется в буфер, затем результат пишется в
        ``data`` слева направо. При равенстве берётся элемент из левого
        участка — так сохраняется исходный порядок равных элементов.
        """
        buffer = list(data[lo:mid])
        i, j, k = 0, mid, lo
        left_len = len(buffer)
        while i < left_len and j < hi:
            if compare(data[j], buffer[i]) < 0:
                data[k] = data[j]
                j += 1
            else:
                data[k] = buffer[i]
                i += 1
            k += 1
        # Остаток правого участка уже стоит на месте; дописываем остаток буфера.
        while i < left_len:
            data[k] = buffer[i]
            i += 1
            k += 1
