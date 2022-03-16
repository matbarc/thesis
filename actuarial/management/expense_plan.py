from dataclasses import dataclass, field


@dataclass
class ExpensePlan:
    pct_premium: float = field(default=0)
    pct_premium_fyo: float = field(default=0)
    flat_fyo: float = field(default=0)
    flat_yearly: float = field(default=0)
    flat_last_year: float = field(default=0)
