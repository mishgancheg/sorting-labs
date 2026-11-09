"""Адаптивная пирамидальная сортировка (adaptive heapsort) Лефкопулоса и Петерссона.

Идея алгоритма: модификация пирамидальной сортировки, чувствительная к
предварительной отсортированности входа. Работа идёт в два этапа.

1. По входу за линейное время строится декартово дерево (Cartesian tree):
   корень — минимальный элемент, левое поддерево строится из элементов
   левее минимума, правое — из элементов правее, и так рекурсивно. В таком
   дереве каждый родитель не больше своих детей, то есть оно само уже
   является кучей, но несбалансированной.
2. Заводится обычная двоичная куча (очередь с приоритетом), в которую
   сначала кладётся только корень декартова дерева. Затем многократно
   извлекается минимум кучи, он отправляется в ответ, а в кучу кладутся
   его дети в декартовом дереве.

Почему это адаптивно: в каждый момент в куче лежат лишь «кандидаты» на
следующий минимум. На почти отсортированном входе декартово дерево похоже
на цепочку, кандидатов мало, и операции с маленькой кучей стоят мало
сравнений. В статье доказано, что число сравнений есть O(n log(Osc/n)),
где Osc — мера «осцилляций» входа; отсюда следует и оптимальность по
числу инверсий: O(n log(Inv/n)). На полностью отсортированном входе
алгоритм тратит O(n) сравнений, в худшем случае — O(n log n).

Ссылки на статьи в каталоге papers/:
- adaptive_heapsort/Adaptive_Heapsort-Levcopoulos-Petersson-1993.pdf
  — оригинальная статья с описанием алгоритма и доказательством
  оптимальности по числу сравнений;
- adaptive_heapsort/A note on adaptive parallel sorting-Levcopoulos-Petersson-1989.pdf
  — ранняя работа тех же авторов о параллельной адаптивной сортировке;
- Exploiting few inversions when sorting__Sequential and parallel
  algorithms-Levcopoulos-Petersson-1996.pdf — обзор класса
  инверсионно-чувствительных алгоритмов.
"""

from __future__ import annotations

from typing import Any, MutableSequence

from sorting_lab.base import Algorithm, AlgorithmInfo, Comparator, default_compare

#: Обозначение отсутствующего ребёнка в декартовом дереве.
_NO_CHILD = -1


class AdaptiveHeapsort(Algorithm):
    """Адаптивная пирамидальная сортировка (Levcopoulos, Petersson, 1993).

    Схема работы:
    1. Построение декартова дерева входа (стековый алгоритм, O(n)).
    2. Извлечение элементов в порядке возрастания через вспомогательную
       двоичную кучу, в которую попадают только дети уже извлечённых узлов.
    """

    def __init__(self) -> None:
        #: Паспорт алгоритма: формальные сведения из статьи-источника.
        self.info = AlgorithmInfo(
            name="adaptive_heapsort",
            full_name="Adaptive Heapsort",
            reference="C. Levcopoulos, O. Petersson, 'Adaptive Heapsort', "
            "Journal of Algorithms 14, 1993; papers/adaptive_heapsort/",
            time_complexity="O(n log n) в худшем случае; O(n log(Osc/n)) и "
            "O(n log(Inv/n)) с учётом отсортированности входа",
            space_complexity="O(n)",
            stable=False,
            in_place=False,
            notes="Декартово дерево хранится в массивах индексов детей; "
            "вспомогательная куча хранит индексы элементов.",
        )

    def sort(self, data: MutableSequence[Any], compare: Comparator = default_compare) -> None:
        """Отсортировать ``data``; полное описание контракта — в ``base.Algorithm.sort``."""
        n = len(data)
        if n < 2:
            return
        items = list(data)
        root, left, right = self._build_cartesian_tree(items, compare)

        # Вспомогательная куча хранит индексы элементов items; на вершине —
        # индекс наименьшего элемента среди текущих кандидатов.
        heap = [root]
        out = 0
        while heap:
            node = self._heap_pop(heap, items, compare)
            data[out] = items[node]
            out += 1
            # Следующий минимум — либо уже в куче, либо один из детей
            # только что извлечённого узла: дети не меньше родителя.
            if left[node] != _NO_CHILD:
                self._heap_push(heap, left[node], items, compare)
            if right[node] != _NO_CHILD:
                self._heap_push(heap, right[node], items, compare)

    @staticmethod
    def _build_cartesian_tree(
        items: list[Any], compare: Comparator
    ) -> tuple[int, list[int], list[int]]:
        """Построить декартово дерево (минимум в корне) за линейное время.

        Стек хранит правую ветвь дерева, построенного по уже просмотренным
        элементам. Новый элемент снимает со стека все строго большие узлы;
        последний снятый становится его левым ребёнком, а сам новый элемент
        становится правым ребёнком узла, оставшегося на вершине стека.
        Каждый индекс попадает в стек и снимается не больше одного раза,
        поэтому число сравнений меньше 2n.

        Возвращает (индекс корня, массив левых детей, массив правых детей).
        """
        n = len(items)
        left = [_NO_CHILD] * n
        right = [_NO_CHILD] * n
        stack: list[int] = []
        for i in range(n):
            last_popped = _NO_CHILD
            while stack and compare(items[i], items[stack[-1]]) < 0:
                last_popped = stack.pop()
            left[i] = last_popped
            if stack:
                right[stack[-1]] = i
            stack.append(i)
        # Дно стека — элемент, который ни разу не был снят: это общий минимум.
        return stack[0], left, right

    @staticmethod
    def _heap_push(heap: list[int], node: int, items: list[Any], compare: Comparator) -> None:
        """Добавить индекс ``node`` в кучу и поднять его до законного места."""
        heap.append(node)
        child = len(heap) - 1
        while child > 0:
            parent = (child - 1) // 2
            if compare(items[heap[child]], items[heap[parent]]) >= 0:
                break
            heap[child], heap[parent] = heap[parent], heap[child]
            child = parent

    @staticmethod
    def _heap_pop(heap: list[int], items: list[Any], compare: Comparator) -> int:
        """Извлечь из кучи индекс наименьшего элемента.

        Последний элемент кучи переносится в корень и просеивается вниз:
        меняется местами с меньшим из детей, пока тот меньше него.
        """
        top = heap[0]
        last = heap.pop()
        size = len(heap)
        if size == 0:
            return top
        heap[0] = last
        parent = 0
        while True:
            smallest = parent
            left = 2 * parent + 1
            right = left + 1
            if left < size and compare(items[heap[left]], items[heap[smallest]]) < 0:
                smallest = left
            if right < size and compare(items[heap[right]], items[heap[smallest]]) < 0:
                smallest = right
            if smallest == parent:
                return top
            heap[parent], heap[smallest] = heap[smallest], heap[parent]
            parent = smallest
