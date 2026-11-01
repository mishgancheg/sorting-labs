"""Реестр алгоритмов проекта.

Реестр — это словарь, сопоставляющий короткому имени алгоритма (например,
``"heapsort"``) его объект. Тесты и измерительный стенд обращаются к
алгоритмам только через реестр, поэтому новый алгоритм, добавленный по
инструкции из ``sorting_lab.algorithms``, автоматически подхватывается везде.

Модуль намеренно не импортирует ``sorting_lab.algorithms`` напрямую (это
делает пакетный ``__init__``), чтобы избежать циклической зависимости:
``algorithms`` импортирует отсюда декоратор ``register``.
"""

from __future__ import annotations

from sorting_lab.base import Algorithm

#: Словарь «короткое имя -> объект алгоритма».
REGISTRY: dict[str, Algorithm] = {}


def register(algorithm: Algorithm) -> Algorithm:
    """Зарегистрировать алгоритм в реестре.

    Аргументы:
        algorithm: объект-наследник :class:`Algorithm` с заполненным паспортом.

    Возвращает тот же объект (удобно использовать как декоратор класса,
    если экземпляр создаётся при объявлении).

    Исключение KeyError — если имя уже занято другим алгоритмом: это защита
    от случайного дублирования имён двумя соавторами.
    """
    name = algorithm.info.name
    if name in REGISTRY:
        raise KeyError(f"Алгоритм с именем '{name}' уже зарегистрирован")
    REGISTRY[name] = algorithm
    return algorithm


def get_algorithm(name: str) -> Algorithm:
    """Получить алгоритм из реестра по короткому имени.

    Исключение KeyError — если имени нет в реестре; текст ошибки перечисляет
    доступные имена, чтобы сразу было видно, что можно запросить.
    """
    try:
        return REGISTRY[name]
    except KeyError:
        available = ", ".join(sorted(REGISTRY)) or "реестр пуст"
        raise KeyError(f"Алгоритм '{name}' не найден. Доступны: {available}") from None


def implemented_algorithms() -> list[Algorithm]:
    """Вернуть только реально реализованные алгоритмы.

    Алгоритм-заготовка (метод ``sort`` бросает NotImplementedError) в список
    не попадает. Используется тестами и измерительным стендом, чтобы не
    работать с ещё не написанными сортировками.
    """
    result: list[Algorithm] = []
    for algorithm in REGISTRY.values():
        probe = [2, 1]
        try:
            algorithm.sort(probe)
        except NotImplementedError:
            continue
        result.append(algorithm)
    return result
