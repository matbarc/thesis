from collections import defaultdict

from actuarial.mortality.table import LifeTable
from actuarial.discounting import Interest
from .benefit import Benefits, CFDic
from .cf_series import RandomCFSeries


class LifeAnnuity(RandomCFSeries):
    pass


class TermLifeAnnuity(LifeAnnuity):
    def __init__(
        self,
        age: int,
        term: int,
        table: LifeTable,
        i: Interest | float,
        due: bool = True,
        amt: int = 1,
    ) -> None:
        self.term = term
        self.amt = amt
        self.due = due
        super().__init__(age, table, i)
        return

    @property
    def benefits(self) -> Benefits:
        death: CFDic = defaultdict(int)
        survival: CFDic = defaultdict(int)

        beg = 0 if self.due else 1
        for yr in range(beg, beg + self.term):
            survival[yr] = self.amt
        return Benefits(death=death, survival=survival)


class WLAnnuity(TermLifeAnnuity):
    def __init__(
        self, age: int, table: LifeTable, i: Interest, due: bool = True, amt: int = 1
    ) -> None:
        term = table.terminal_age - age
        super().__init__(age, term, table, i, due, amt)
        return
