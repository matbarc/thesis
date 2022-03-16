from ..products.insurance import Insurance
from ..products.annuity import LifeAnnuity
from ..mortality.table import LifeTable
from .expense_plan import ExpensePlan

import numpy as np
from sympy import solve
from sympy.abc import p

from typing import NamedTuple


class BenefitCurve(NamedTuple):
    death: np.typing.NDArray
    survival: np.typing.NDArray


class Person(NamedTuple):
    age: int
    table: LifeTable


class Policy:
    def __init__(
        self,
        insured: Person,
        benefits: list[Insurance],
        annuity: LifeAnnuity,
        expense_plan: ExpensePlan,
    ):
        self.insured = insured
        self.benefits = benefits
        self.annuity = annuity
        self.expense_plan = expense_plan
        return

    @property
    def gross_premium(self) -> float:
        return self._premium(exp=self.expense_plan)

    @property
    def net_premium(self) -> float:
        return self._premium(exp=ExpensePlan(0, 0, 0, 0, 0))

    # def benefit_curve(self, t: int) -> BenefitCurve:
    #     age = self.insured.age

    #     death = np.sum([ben.death_benefits(age) for ben in self.benefits], axis=0)
    #     survival = np.sum([ben.survival_benefits(age) for ben in self.benefits], axis=0)
    #     return BenefitCurve(death[t:], survival[t:])

    def payment_curve(self, t: int) -> list[float]:
        return self.annuity.payments(t)

    def net_reserve(self, t: int) -> float:
        return self._ben_epv(t) - self.net_premium * self.annuity.epv(t)

    def gross_reserve(self, t: int) -> float:
        return self.net_reserve(t) + self.expense_reserve(t)

    def expense_reserve(self, t: int) -> float:
        expense_load = self.gross_premium - self.net_premium
        return expense_load * self.annuity.epv(t)

    def nar(self, t: int) -> float:
        return 0

    def _premium(self, exp: ExpensePlan) -> float:
        ann = self.annuity.epv()

        exp_total = (
            exp.flat_fyo
            + exp.flat_yearly * ann
            + p * (exp.pct_premium * ann + exp.pct_premium_fyo)
        )
        loss = self._ben_epv() - (p * ann) + exp_total
        return solve(loss)

    def _ben_epv(self, t: int = 0) -> float:
        return sum([prod.epv(t) for prod in self.benefits])
