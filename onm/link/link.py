from abc import ABC, abstractmethod


class Link(ABC):
    @abstractmethod
    def get_access_token(self) -> str:
        pass

    @abstractmethod
    def update_link(self, access_token: str) -> None:
        pass
