from abc import ABC, abstractmethod

class AnalyticsRepository(ABC):
    @abstractmethod
    def run_query(self, query:str) -> dict:
        pass
