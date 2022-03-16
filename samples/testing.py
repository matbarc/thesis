from actuarial.products.insurance import (
    ComboInsurance,
    TermInsurance,
    PureEndowmentInsurance,
    EndowmentInsurance,
)
from actuarial.mortality.table import SULT

age = 30
term = 10
table = SULT
i = 0.05


end1 = EndowmentInsurance(age, term, table, i)
prods = [
    TermInsurance(age, term, table, i),
    PureEndowmentInsurance(age, term, table, i),
]
end2 = ComboInsurance(products=prods)

print(end1.epv())
print(end2.epv())
