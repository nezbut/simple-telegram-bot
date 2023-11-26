class CommandExists(Exception):

    def __str__(self) -> str:
        return "Такая команда у бота уже существует."

class CommandIsNotCoroutine(Exception):

    def __str__(self) -> str:
        return "Команда не является корутиной."

class MinimumOneArgument(Exception):

    def __str__(self) -> str:
        return "Минимум должен быть один аргумент для передачи экземпляра класса UserMessage."

__all__ = (
    'CommandExists',
    'CommandIsNotCoroutine',
    'MinimumOneArgument'
)