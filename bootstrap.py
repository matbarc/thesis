import pandas as pd
from actuarial.db.mappings.lives import LifeTableRow
from actuarial.db.mappings.table import LifeTable
from actuarial.db.session import session_fac

df = pd.read_csv("tabua.csv", delimiter=";", usecols=["masc", "fem"])  # type: ignore

to_insert = []
for age, (masc, fem) in df.iterrows():
    to_insert += [
        LifeTableRow(table_id=0, age=age, lives=masc),
        LifeTableRow(table_id=1, age=age, lives=fem),
    ]

to_insert_tables = [LifeTable(name="BR-m"), LifeTable("BR-f")]

session = session_fac()
session.add_all(to_insert_tables)
session.add_all(to_insert)
session.commit()
