from abc import ABC, abstractmethod

import numpy as np

from actuarial.discounting import Interest, FixedInterest
from actuarial.mortality.table import LifeTable
from .benefit import Benefits

IntInput = Interest | float
Array = np.typing.NDArray


class RandomCFSeries(ABC):
    def __init__(self, age: int, table: LifeTable, i: IntInput) -> None:
        self.age = age
        self.table = table
        self.int = i if isinstance(i, Interest) else FixedInterest(i)
        self.yrs_to_omega = table.terminal_age - age
        return

    @property
    @abstractmethod
    def benefits(self) -> Benefits:
        ...

    def epv(self, t: int = 0) -> float:
        outcomes, probs = self.distribution(t)
        return moment(1, outcomes, probs)

    def var(self, t: int = 0) -> float:
        outcomes, probs = self.distribution(t)
        return moment(2, outcomes, probs) - moment(1, outcomes, probs) ** 2

    def year_t_benefit_pv(self, death_t: int) -> float:
        surv_b, death_b = self.benefits

        death_ben_pv = self.int.disc(t0=0, n=death_t + 1) * death_b[death_t]
        surv_ben_pv = sum(
            [
                amount * self.int.disc(t0=0, n=year)
                for (year, amount) in surv_b.items()
                if year <= death_t
            ]
        )
        return death_ben_pv + surv_ben_pv

    def distribution(self, t: int = 0) -> tuple[Array, Array]:
        new_age = self.age + t
        support = range(t, self.yrs_to_omega)
        outcomes = np.array([self.year_t_benefit_pv(yr) for yr in support])
        probs = np.array([self.table.q_def(new_age, 1, i) for i in support])
        return outcomes, probs


def moment(k: int, outcomes: Array, probs: Array) -> float:
    if not len(outcomes) == len(probs):
        raise ValueError("Size of outcome array must match probability array")

    return np.sum(np.power(outcomes, k) * probs)
