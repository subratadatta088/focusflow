from abc import ABC, abstractmethod

class EvalType(ABC):
    def __init__(self, rule):
        self.rule = rule

    @abstractmethod
    def evaluate(self, context) -> int:
        """
        Evaluates the rule and returns score delta (+/-).
        """
        pass
