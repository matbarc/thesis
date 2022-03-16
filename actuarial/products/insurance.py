from collections import defaultdict

from actuarial.discounting import Interest
from actuarial.mortality.table import LifeTable
from .benefit import Benefits, CFDic
from .cf_series import RandomCFSeries

IntInput = Interest | float


class Insurance(RandomCFSeries):
    pass


class TermInsurance(Insurance):
    def __init__(
        self, age: int, term: int, table: LifeTable, i: IntInput, amt: float = 1
    ) -> None:
        self.term = term
        self.amt = amt
        super().__init__(age, table, i)
        return

    @property
    def benefits(self) -> Benefits:
        death: CFDic = defaultdict(int)
        survival: CFDic = defaultdict(int)
        for yr in range(self.term):
            death[yr] = self.amt
        return Benefits(death=death, survival=survival)


class WLInsurance(TermInsurance):
    def __init__(self, age: int, table: LifeTable, i: IntInput, amt: float = 1) -> None:
        term = table.terminal_age - age
        super().__init__(age, term, table, i, amt)
        return


class PureEndowmentInsurance(Insurance):
    def __init__(
        self, age: int, term: int, table: LifeTable, i: IntInput, amt: float = 1
    ) -> None:
        self.term = term
        self.amt = amt
        super().__init__(age, table, i)
        return

    @property
    def benefits(self) -> Benefits:
        death: CFDic = defaultdict(int)
        survival: CFDic = defaultdict(int)
        survival[self.term] = self.amt
        return Benefits(death=death, survival=survival)


class EndowmentInsurance(Insurance):
    def __init__(
        self, age: int, term: int, table: LifeTable, i: IntInput, amt: float = 1
    ) -> None:
        super().__init__(age, table, i)
        self.pure_end = PureEndowmentInsurance(age, term, table, i, amt)
        self.term_ins = TermInsurance(age, term, table, i, amt)
        return

    @property
    def benefits(self) -> Benefits:
        return self.pure_end.benefits + self.term_ins.benefits


class ComboInsurance(Insurance):
    def __init__(self, products: list[Insurance]) -> None:
        self.products = products
        age, table, i = self.assert_inputs_equal()

        super().__init__(age, table, i)
        return

    @property
    def benefits(self) -> Benefits:
        bens = [prod.benefits for prod in self.products]
        return sum(bens)

    def assert_inputs_equal(self) -> tuple[int, LifeTable, Interest]:
        ages = {prod.age for prod in self.products}
        tables = {prod.table for prod in self.products}
        ints = {prod.int for prod in self.products}

        if not len(ages) == len(tables) == len(ints) == 1:
            msg = "This can only be used if the ages, tables and interests are equal."
            print(ages, tables, ints)
            raise ValueError(msg)

        return ages.pop(), tables.pop(), ints.pop()
