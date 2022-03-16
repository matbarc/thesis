from abc import ABC, abstractmethod
from actuarial.mortality.table import LifeTable


import numpy as np
from numpy.typing import ArrayLike


class Interest(ABC):
    @abstractmethod
    def disc(self, t0: int, n: int) -> float:
        ...

    @abstractmethod
    def comp(self, t0: int, n: int) -> float:
        ...

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self.i == other.i

    def __hash__(self) -> int:
        return hash(self.i)

    def disc_vec(self, t0: int, n: int) -> list[float]:
        return [self.disc(t0, i) for i in range(1, n + 1)]


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


class InterestVec(Interest):
    def __init__(self, i: ArrayLike) -> None:
        self.i = np.array(i)
        return

    def comp(self, t0: int, n: int) -> float:
        return (1 + self.i)[t0 : t0 + n].prod()

    def disc(self, t0: int, n: int) -> float:
        return 1 / self.comp(t0, n)


def E(age: int, k: int, table: LifeTable, i: Interest) -> float:
    return table.p(age, k) * i.disc(age, k)
