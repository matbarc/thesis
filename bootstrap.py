from pathlib import Path

from actuarial.db.session import Session
from actuarial.db.session import engine, Base
from actuarial.db.mappings.table import DBLifeTable
from actuarial.db.mappings.lives import LifeTableRow
from actuarial.mortality.import_csv import import_csv

TABLES_DIR = "data/tables"


with open("tables.db", "w+") as fp:
    pass

Base.metadata.create_all(bind=engine)

table_paths = Path(TABLES_DIR).glob("*")

to_insert = []

for path in table_paths:
    table = DBLifeTable(name=path.stem)
    rows = import_csv(path)
    table.rows.extend(rows)
    to_insert.append(table)


with Session.begin() as session:
    session.add_all(to_insert)
    session.commit()
