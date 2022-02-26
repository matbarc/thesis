from dataclasses import dataclass


@dataclass
class ExpensePlan:
    # (inception, a)
    percent_rec: float
    percent_beg: float
    lump_rec: float
    lump_beg: float
