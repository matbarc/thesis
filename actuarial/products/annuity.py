from abc import ABC, abstractmethod
from actuarial.db.mappings.table import LifeTable
from actuarial.discounting import Interest, E


class LifeAnnuity(ABC):
    """docstring for LifeAnnuity."""

    @abstractmethod
    def epv(self, age) -> float:
        ...


class LifeAnnuityDue(LifeAnnuity):
    def __init__(self, dist: LifeTable, i: Interest) -> None:
        self.dist = dist
        self.int = i
        return

    def epv(self, age: int) -> float:
        exp_payments = [E(age, i, self.dist, self.int) for i in range(100)]
        return sum(exp_payments)


class TermLifeAnnuityDue(LifeAnnuity):
    def __init__(self, term: int, dist: LifeTable, i: Interest) -> None:
        self.dist = dist
        self.int = i
        self.term = term
        return

    def epv(self, age: int) -> float:
        exp_payments = [E(age, i, self.dist, self.int) for i in range(self.term)]
        return sum(exp_payments)


class WholeLifeAnnuityImmediate(LifeAnnuity):
    def __init__(self, dist: LifeTable, i: Interest) -> None:
        self.dist = dist
        self.int = i
        return

    def epv(self, age: int) -> float:
        exp_payments = [E(age, i, self.dist, self.int) for i in range(1, 101)]
        return sum(exp_payments)


class TermLifeAnnuityImmediate(LifeAnnuity):
    def __init__(self, term: int, dist: LifeTable, i: Interest) -> None:
        self.dist = dist
        self.int = i
        self.term = term
        return

    def epv(self, age: int) -> float:
        exp_payments = [E(age, i, self.dist, self.int) for i in range(1, self.term)]
        return sum(exp_payments)
