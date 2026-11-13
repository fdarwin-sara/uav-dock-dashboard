from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable

from app.models.state import DashboardSnapshot


class IDataProvider(ABC):
    @abstractmethod
    def snapshot(self) -> DashboardSnapshot:
        raise NotImplementedError

    @abstractmethod
    def subscribe(self, callback: Callable[[DashboardSnapshot], None]) -> None:
        raise NotImplementedError

    @abstractmethod
    def start(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def stop(self) -> None:
        raise NotImplementedError

