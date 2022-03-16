from typing import Literal
from actuarial.mortality.table import LifeTable
from actuarial.products.insurance import (
    TermInsurance,
    WLInsurance,
    EndowmentInsurance,
    PureEndowmentInsurance,
)
from actuarial.products.annuity import WLAnnuity, TermLifeAnnuity


def get_policy(
    product: Literal["WL", "Term", "PureEndowment", "Endowment"],
    age: int,
    table: LifeTable,
    i: float,
    term: int = -1,
    amount: float = 1,
) -> float:

    cls = {
        "WL": WLInsurance,
        "Term": TermInsurance,
        "PureEnd": PureEndowmentInsurance,
        "End": EndowmentInsurance,
    }
    inst = (
        cls[product](age, term, table, i, amount)
        if product != "WL"
        else cls[product](age, table, i, amount)
    )

    return inst


def get_annuity(
    age: int, term: int, table: LifeTable, i: float, amount: float = 1
) -> float:
    if term == -1:
        inst = WLAnnuity(age, table, i)
    else:
        inst = TermLifeAnnuity(age, term, table, i)

    return inst
