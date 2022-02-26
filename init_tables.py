from actuarial.db.session import engine, Base
from actuarial.db.mappings.lives import LifeTableRow
from actuarial.db.mappings.table import LifeTable

with open("tables.db", "w+") as fp:
    pass

Base.metadata.create_all(bind=engine)
