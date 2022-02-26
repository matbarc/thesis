from ..products.insurance import Insurance
from ..products.annuity import LifeAnnuity
from .expense_plan import ExpensePlan

from sympy import solve
from sympy.abc import p


class Policy:
    def __init__(
        self, ins: Insurance, ann: LifeAnnuity, exp: ExpensePlan, age: int
    ) -> None:
        self.ins = ins
        self.ann = ann
        self.exp = exp
        self.age = age
        return

    # for now assumes equivalent principle
    @property
    def premium(self) -> float:
        ann = self.ann.epv(self.age)

        exp_total = (
            self.exp.lump_beg
            + self.exp.lump_rec * ann
            + p * (self.exp.percent_rec * ann + self.exp.percent_beg)
        )
        loss = self.ins.epv(self.age) - (p * ann) + exp_total

        return solve(loss)
