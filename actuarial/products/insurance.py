from actuarial.db.mappings.table import LifeTable
from actuarial.discounting import E, Interest
from abc import ABC, abstractmethod


class Insurance(ABC):
    @abstractmethod
    def epv(self, age: int) -> float:
        ...

    # @abstractmethod
    # def var(self, age: int) -> float:
    #     ...


class DiscreteWLInsurance(Insurance):
    def __init__(self, dist: LifeTable, i: Interest) -> None:
        self.dist = dist
        self.int = i
        return

    def epv(self, age: int) -> float:
        expected_payouts = [
            self.dist.q_def(age, 1, i) * self.int.disc(age, i) for i in range(100)
        ]
        return sum(expected_payouts)

    # def var(self, age: int) -> float:
    #     expected_payouts = [
    #         self.dist.q_def(age, 1, i) * self.int.disc(2 * i) for i in range(100)
    #     ]
    #     return sum(expected_payouts)


class DiscreteTermInsurance(Insurance):
    def __init__(self, term: int, dist: LifeTable, i: Interest) -> None:
        self.dist = dist
        self.int = i
        self.term = term
        return

    def epv(self, age: int) -> float:
        expected_payouts = [
            self.dist.q_def(age, 1, i) * self.int.disc(age, i + 1)
            for i in range(self.term)
        ]
        return sum(expected_payouts)

    # def var(self, age: int) -> float:
    #     expected_payouts = [
    #         self.dist.q_def(age, 1, i) * self.int.disc(2 * i + i**2 + 1)
    #         for i in range(self.term)
    #     ]
    #     return sum(expected_payouts)


class DiscreteEndowmentInsurance(Insurance):
    def __init__(self, term: int, dist: LifeTable, i: Interest) -> None:
        self.dist = dist
        self.int = i
        self.term = term

        self.term_ins = DiscreteTermInsurance(term, dist, i)
        return

    def epv(self, age: int) -> float:
        return self.term_ins.epv(age) + E(age, self.term, self.dist, self.int)

    # def var(self, age: int) -> float:
    #     return self.term_ins.var(age) + E(age, self.term, self.dist, self.int * 2)
