"""Реестр алгоритмов: единая точка доступа ко всем сортировкам проекта.

Модуль ``algorithms`` собирает реализации, а ``registry`` хранит их в словаре
``REGISTRY``. Схема работы при добавлении нового алгоритма:

1. Создаётся файл ``src/sorting_lab/algorithms/<имя>.py`` с классом-наследником
   ``Algorithm``.
2. Класс импортируется здесь, в ``__init__.py``.
3. Экземпляр класса регистрируется декоратором ``@register`` из модуля
   ``registry``.

После этого алгоритм автоматически участвует в тестах корректности
(см. ``tests/test_algorithms.py``) и доступен измерительному стенду.
"""

from sorting_lab.algorithms.adaptive_heapsort import AdaptiveHeapsort
from sorting_lab.algorithms.heapsort import Heapsort
from sorting_lab.algorithms.introsort import Introsort
from sorting_lab.algorithms.powersort import Powersort
from sorting_lab.algorithms.splitsort import Splitsort
from sorting_lab.registry import register

# Регистрация всех алгоритмов проекта. Порядок перечисления — алфавитный.
register(AdaptiveHeapsort())
register(Heapsort())
register(Introsort())
register(Powersort())
register(Splitsort())

__all__ = [
    "AdaptiveHeapsort",
    "Heapsort",
    "Introsort",
    "Powersort",
    "Splitsort",
    "register",
]
