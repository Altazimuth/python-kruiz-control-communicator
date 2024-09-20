from abc import ABC, abstractmethod

class PluginInterface(ABC):
    def __init__(self):
        self.active = True

    def __bool__(self):
        return self.active

    @property
    @abstractmethod
    def name() -> str:
        pass

    @abstractmethod
    def handle_event(self, event_message: str, event_data: str) -> bool:
        pass

    @abstractmethod
    def init(self) -> bool:
        pass
