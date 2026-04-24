from collections import defaultdict
from typing import Callable

_handlers: dict[str, list[Callable]] = defaultdict(list)

def on(evento: str, handler: Callable) -> None:
    _handlers[evento].append(handler)

def off(evento: str, handler: Callable) -> None:
    _handlers[evento] = [h for h in _handlers[evento] if h != handler]

def emit(evento: str, **kwargs) -> None:
    for handler in list(_handlers[evento]):
        try:
            handler(**kwargs)
        except Exception:
            pass
