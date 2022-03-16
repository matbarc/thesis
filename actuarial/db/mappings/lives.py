from typing import TYPE_CHECKING

from sqlalchemy import Column, Integer, ForeignKey, Float

from sqlalchemy.orm import relationship

from ..session import Base
from ...utils import generic_class_repr

if TYPE_CHECKING:
    from .table import DBLifeTable


class LifeTableRow(Base):
    __tablename__ = "lives"

    table_id: int = Column(Integer, ForeignKey("tables.id"), primary_key=True)
    age: int = Column(Integer, primary_key=True)
    lives: float = Column(Float, primary_key=True)

    table: "DBLifeTable" = relationship("DBLifeTable", back_populates="rows")

    def __repr__(self) -> str:
        return generic_class_repr(self)
