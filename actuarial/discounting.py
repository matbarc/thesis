from abc import ABC, abstractmethod
from actuarial.db.mappings.table import LifeTable


import numpy as np
from numpy.typing import ArrayLike


class Interest(ABC):
    @abstractmethod
    def disc(self, t0: int, n: int) -> float:
        pass

    @abstractmethod
    def comp(self, t0: int, n: int) -> float:
        pass


class FixedInterest(Interest):
    def __init__(self, i: float) -> None:
        self.i = i
        return

    def comp(self, t0: int, n: int) -> float:
        return (1 + self.i) ** n

    def disc(self, t0: int, n: int) -> float:
        return self.v() ** n

    def v(self) -> float:
        return 1 / (1 + self.i)

    # def __mul__(self, other: Union[int, float]) -> "FixedInterest":
    #     if not isinstance(other, (float, int)):
    #         TypeError("Interest multiplication is only defined for numbers.")
    #     return FixedInterest(self.i * other)


class InterestVec(Interest):
    def __init__(self, i: np.typing.ArrayLike) -> None:
        self.i = np.array(i)
        return

    def comp(self, t0: int, n: int) -> float:
        return (1 + self.i)[t0 : t0 + n].prod()

    def disc(self, t0: int, n: int) -> float:
        return 1 / self.comp(t0, n)


def E(age: int, k: int, table: LifeTable, i: Interest) -> float:
    return table.p(age, k) * i.disc(age, k)
