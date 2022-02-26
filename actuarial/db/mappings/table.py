from typing import TYPE_CHECKING

from sqlalchemy import String, Integer, Column, orm
from sqlalchemy.orm import relationship

from ..session import Base
from ...utils import generic_class_repr

if TYPE_CHECKING:
    from .lives import LifeTableRow


class LifeTable(Base):
    __tablename__ = "tables"

    id: int = Column(Integer(), primary_key=True, autoincrement=True)
    name: str = Column(String(30))
    rows: list["LifeTableRow"] = relationship(
        "LifeTableRow", cascade="all, delete-orphan", uselist=True
    )

    def __init__(self, name: str) -> None:
        self.name = name
        return

    @orm.reconstructor
    def init_on_load(self) -> None:
        self.lives = [row.lives for row in self.rows]
        return

    def p(self, age: int, k: int = 1) -> float:
        if not self._inputs_valid(age, k):
            return 0
        elif k == 0:
            return 1

        return self.lives_at(age + k) / self.lives_at(age)

    def q(self, age: int, k: int = 1) -> float:
        return 1 - self.p(age, k)

    def q_def(self, age: int, k: int, deferral: int) -> float:
        """Probability that (age) lives deferral and dies in k years"""
        return self.p(age, deferral) * self.q(age + deferral, k)

    def lives_at(self, age: int) -> float:
        return self.lives[age]

    def _inputs_valid(self, age: int, k: int) -> bool:
        if age < 20 or (age + k) > 111:
            return False
        return True

    def __repr__(self) -> str:
        return generic_class_repr(self)
