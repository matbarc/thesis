from sqlalchemy import select
from actuarial.db.mappings.table import DBLifeTable
from actuarial.db.mappings.lives import LifeTableRow
from actuarial.db.session import Session
from actuarial.utils import generic_class_repr


class LifeTable:
    def __init__(self, name: str, lives: list[float]) -> None:
        self.name = name
        self.lives = lives
        return

    @classmethod
    def from_db(cls, orm_obj: DBLifeTable) -> "LifeTable":
        lives = [row.lives for row in orm_obj.rows]
        return cls(orm_obj.name, lives)

    def to_db(self) -> "DBLifeTable":
        rows = [LifeTableRow(age=i, lives=l) for i, l in enumerate(self.lives)]
        obj = DBLifeTable(name=self.name)
        obj.rows.extend(rows)
        return obj

    @property
    def terminal_age(self) -> int:
        return len(self.lives) - 1

    def p(self, age: int, k: int = 1) -> float:
        if not self._inputs_valid(age, k):
            return 0
        elif k == 0:
            return 1

        try:
            return self.lives_at(age + k) / self.lives_at(age)
        except ZeroDivisionError:
            raise ZeroDivisionError(f"{age+k}, {age}, {self.terminal_age}")

    def q(self, age: int, k: int = 1) -> float:
        return 1 - self.p(age, k)

    def q_def(self, age: int, k: int, deferral: int) -> float:
        """Probability that (age) lives deferral and dies in k years"""
        return self.p(age, deferral) * self.q(age + deferral, k)

    def lives_at(self, age: int) -> float:
        return self.lives[age]

    def _inputs_valid(self, age: int, k: int) -> bool:
        if age < 0 or (age + k) >= self.terminal_age:
            return False
        return True

    def __repr__(self) -> str:
        return generic_class_repr(self, exclude=["lives"])


class TableNotFound(Exception):
    pass


def get_tables() -> dict[str, LifeTable]:
    stmt = stmt = select(DBLifeTable)
    with Session.begin() as session:
        query = session.execute(stmt).scalars()
        dic = {orm_table.name: LifeTable.from_db(orm_table) for orm_table in query}
    return dic


def get_table_names() -> list[str]:
    stmt = stmt = select(DBLifeTable.name)
    with Session.begin() as session:
        names = list(session.execute(stmt).scalars())
    return names


def get_table_by_name(name: str) -> LifeTable:
    stmt = stmt = select(DBLifeTable).filter_by(name=name)
    with Session.begin() as session:
        orm_table = session.execute(stmt).scalar_one_or_none()

        if not orm_table:
            raise TableNotFound(f"No table found with name: {name}.")

        return LifeTable.from_db(orm_table)


SULT = get_table_by_name("SULT")
BR_m = get_table_by_name("BR-m")
BR_f = get_table_by_name("BR-f")
