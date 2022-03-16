from sqlalchemy import String, Integer, Column
from sqlalchemy.orm import relationship

from ..session import Base
from .lives import LifeTableRow


class DBLifeTable(Base):
    __tablename__ = "tables"

    id: int = Column(Integer(), primary_key=True, autoincrement=True)
    name: str = Column(String(30))
    rows: list["LifeTableRow"] = relationship(
        "LifeTableRow", cascade="all, delete-orphan", uselist=True
    )

    def __init__(self, name: str) -> None:
        self.name = name
        return
