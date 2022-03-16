from pathlib import Path

import pandas as pd

from actuarial.db.mappings.lives import LifeTableRow as Row


class BadFormatting(Exception):
    ...


def import_csv(path: Path) -> list[Row]:
    try:
        df = pd.read_csv(  # type: ignore
            path,
            dtype={"age": "Int32", "lives": "Float32"},
            header=0,
            usecols=["age", "lives"],
            sep=";",
        )
    except ValueError:
        raise BadFormatting("Could not parse CSV properly. Check formatting.")

    if not df["age"].diff().eq(1).all:
        raise BadFormatting("Ages not sequential. Check formatting.")
    if not df["lives"].is_monotonic_decreasing:
        raise BadFormatting("Lives sequence is not decreasing.")

    rows = [Row(age=age, lives=lives) for index, (age, lives) in df.iterrows()]
    return rows
