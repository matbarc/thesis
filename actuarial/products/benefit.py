from typing import NamedTuple, DefaultDict
from collections import defaultdict

CFDic = DefaultDict[int, float]


class Benefits(NamedTuple):
    survival: CFDic = defaultdict(float)
    death: CFDic = defaultdict(float)

    def __add__(self, other: object) -> "Benefits":
        if other == 0:
            return self

        elif not isinstance(other, Benefits):
            raise TypeError(
                f"Can only add other 'Benefits' instances (Got {type(other)})."
            )

        death = join_dicts(self.death, other.death)
        survival = join_dicts(self.survival, other.survival)
        return Benefits(survival=survival, death=death)

    def __radd__(self, other: object) -> "Benefits":
        return self.__add__(other)


def join_dicts(dic1: CFDic, dic2: CFDic) -> CFDic:
    for yr, amt in dic2.items():
        dic1[yr] += amt
    return dic1
