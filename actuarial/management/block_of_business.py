import numpy as np

from .policy import Policy

NPArray = np.typing.NDArray
Distribution = tuple[NPArray, NPArray]


class BlockOfBusiness:
    def __init__(self, name: str, policies: list[Policy]) -> None:
        self.name = name
        self.policies: list[Policy] = []
        return

    def add_policy(self, policy: Policy) -> None:
        self.policies.append(policy)
        return

    def age_dist(self) -> Distribution:
        age_list = [pol.insured.age for pol in self.policies]
        ages, counts = np.unique(age_list, return_counts=True)
        return ages, counts

    def nar_dist(self, bin_size: int = 100_000) -> Distribution:
        return

    @property
    def lives(self) -> int:
        return len(self.policies)
