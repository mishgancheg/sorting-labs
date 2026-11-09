"""Splitsort — адаптивная сортировка Лефкопулоса и Петерссона (1991).

Идея алгоритма. «Адаптивная» означает, что время работы зависит не только
от числа элементов n, но и от предварительной отсортированности входа:
чем ближе вход к отсортированному, тем быстрее работает алгоритм.

Splitsort основан на методе Кука и Кима. Вход просматривается слева
направо, и при этом поддерживается восходящая подпоследовательность
(upsequence), устроенная как стек. Очередной элемент сравнивается с
вершиной стека («головой»). Если он меньше головы, то эти два элемента
образуют неупорядоченную пару: оба удаляются, и головой становится
предыдущий элемент стека. Иначе элемент кладётся на стек. После
просмотра в стеке остаётся отсортированная подпоследовательность.

Удалённые элементы делятся на две группы: Xg — большие элементы своих
пар, Xs — меньшие. Порядок внутри групп совпадает с порядком во входе.
Обе группы сортируются рекурсивно, а затем три отсортированные
последовательности сливаются. Статья доказывает, что суммарное число
инверсий (пар элементов в неправильном порядке) в Xg и Xs не больше 2/3
от числа инверсий во входе. Отсюда оценка 4.6 n log(Inv/n) + O(n)
сравнений, а в худшем случае — не более 2.5 n log2 n.

Реализован основной вариант из статьи (раздел 3) с дополнительной
памятью O(n); вариант «на месте» из раздела 5 не реализован.

Ссылки на статьи в каталоге papers/:
- splitsort/Splitsort_an adaptive sorting algorithm-Levcopoulos-Petersson-1991.pdf
  — оригинальная статья с описанием алгоритма и доказательством оценок;
- adaptive_heapsort/Adaptive_Heapsort-Levcopoulos-Petersson-1993.pdf
  — родственная работа тех же авторов, полезна для сравнения подходов.
"""

from __future__ import annotations

from typing import Any, MutableSequence

from sorting_lab.base import Algorithm, AlgorithmInfo, Comparator, default_compare

# Метки принадлежности элемента после разделения (Split).
_UP = 0  # остался в восходящей подпоследовательности
_GREATER = 1  # больший элемент удалённой пары, попадает в Xg
_SMALLER = 2  # меньший элемент удалённой пары, попадает в Xs


class Splitsort(Algorithm):
    """Адаптивная сортировка Splitsort (Levcopoulos, Petersson, 1991).

    Схема работы (процедура Splitsort из статьи):
    1. Split: выделение восходящей подпоследовательности и удаление
       неупорядоченных пар, разделение удалённых на Xg и Xs.
    2. Рекурсивная сортировка Xg и Xs.
    3. Merge: слияние трёх отсортированных последовательностей; сначала
       Xs сливается с более короткой из двух других, затем результат —
       с оставшейся (так меньше сравнений, см. лемму 2 статьи).
    """

    def __init__(self) -> None:
        #: Паспорт алгоритма: формальные сведения из статьи-источника.
        self.info = AlgorithmInfo(
            name="splitsort",
            full_name="Splitsort: an adaptive sorting algorithm",
            reference="C. Levcopoulos, O. Petersson, 'Splitsort — an adaptive "
            "sorting algorithm', Information Processing Letters, 1991; "
            "papers/splitsort/",
            time_complexity="O(n log n) в худшем случае (не более 2.5 n log n "
            "сравнений); O(n log(Inv/n)) с учётом числа инверсий Inv",
            space_complexity="O(n)",
            stable=False,
            in_place=False,
            notes="Основной вариант статьи (раздел 3) с памятью O(n); "
            "вариант на месте (раздел 5) не реализован.",
        )

    def sort(self, data: MutableSequence[Any], compare: Comparator = default_compare) -> None:
        """Отсортировать ``data``; полное описание контракта — в ``base.Algorithm.sort``."""
        if len(data) < 2:
            return
        result = self._splitsort(list(data), compare)
        data[:] = result

    def _splitsort(self, items: list[Any], compare: Comparator) -> list[Any]:
        """Вернуть отсортированную копию списка ``items`` (рекурсивная часть)."""
        if len(items) < 2:
            return items
        upsequence, greater, smaller = self._split(items, compare)
        # Длина каждой из групп Xg и Xs не больше n / 2, поэтому глубина
        # рекурсии не превышает log2(n).
        greater = self._splitsort(greater, compare)
        smaller = self._splitsort(smaller, compare)
        return self._merge3(upsequence, greater, smaller, compare)

    @staticmethod
    def _split(
        items: list[Any], compare: Comparator
    ) -> tuple[list[Any], list[Any], list[Any]]:
        """Разделение Кука–Кима: вернуть (восходящая часть, Xg, Xs).

        Восходящая подпоследовательность хранится как стек индексов. Для
        каждого элемента запоминается метка группы, а в конце один проход
        по меткам раскладывает элементы по трём спискам. Так все три списка
        получаются в порядке исходного входа (разделение устойчиво), что
        нужно для доказательства леммы 5 статьи. Без меток элементы Xg
        оказались бы в другом порядке: они снимаются с вершины стека.
        """
        labels = [_UP] * len(items)
        stack = [0]
        for i in range(1, len(items)):
            if stack and compare(items[i], items[stack[-1]]) < 0:
                # Новый элемент меньше головы: удаляем пару (голова, новый).
                head = stack.pop()
                labels[head] = _GREATER
                labels[i] = _SMALLER
            else:
                stack.append(i)

        upsequence: list[Any] = []
        greater: list[Any] = []
        smaller: list[Any] = []
        groups = (upsequence, greater, smaller)
        for item, label in zip(items, labels):
            groups[label].append(item)
        return upsequence, greater, smaller

    def _merge3(
        self,
        upsequence: list[Any],
        greater: list[Any],
        smaller: list[Any],
        compare: Comparator,
    ) -> list[Any]:
        """Слить три отсортированных списка в порядке, предложенном в статье."""
        if len(greater) <= len(upsequence):
            return self._merge2(self._merge2(smaller, greater, compare), upsequence, compare)
        return self._merge2(self._merge2(smaller, upsequence, compare), greater, compare)

    @staticmethod
    def _merge2(first: list[Any], second: list[Any], compare: Comparator) -> list[Any]:
        """Слить два отсортированных списка в новый отсортированный список."""
        result: list[Any] = []
        i = j = 0
        while i < len(first) and j < len(second):
            if compare(second[j], first[i]) < 0:
                result.append(second[j])
                j += 1
            else:
                result.append(first[i])
                i += 1
        result.extend(first[i:])
        result.extend(second[j:])
        return result
