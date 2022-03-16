import PySimpleGUI as sg
from dataclasses import dataclass
import csv

# from sqlalchemy import select
# from matplotlib import ticker, rcParams
# from matplotlib.pyplot import subplots
# from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# from actuarial.discounting import FixedInterest
# from actuarial.db.session import session_fac
# from actuarial.db.mappings.table import LifeTable
# from actuarial.products.insurance import WLInsurance, TermInsurance
# from actuarial.products.annuity import LifeAnnuity, TermLifeAnnuity


WINDOW_TITLE = "PLACEHOLDER TITLE"
NUM_ROWS = 20


@dataclass
class Employee:
    first: str
    last: str
    ein: str
    legacy: str
    dept: str


def read_csv():
    with open("data/MOCK_DATA.csv") as fp:
        rd = csv.DictReader(fp)
        return [
            Employee(
                ein=row["ein"],
                first=row["first_name"],
                last=row["last_name"],
                dept=row["department"],
                legacy=row["legacy"],
            )
            for row in rd
        ]


def build_treedata(employees: list[Employee]):
    treedata = sg.TreeData()

    treedata.insert(
        parent="",
        key="legacy",
        text="Legacy Group",
        values=[],
    )
    treedata.insert(
        parent="",
        key="new",
        text="New Sales Group",
        values=[],
    )

    for employee in employees:
        treedata.insert(
            parent="legacy" if employee.legacy == "true" else "new",
            key=employee.ein,
            text=f"{employee.last}, {employee.first}",
            values=[employee.dept],
        )
    return treedata


def get_layout(treedata):
    headings = ["Department"]

    layout = [
        [
            sg.Tree(
                data=treedata,
                num_rows=NUM_ROWS,
                key="tree",
                headings=headings,
                col0_width=40,
            )
        ],
        [sg.Button("Import", enable_events=True, key="import")],
    ]
    return layout


def main():
    treedata = build_treedata([])

    # define the form layout
    layout = get_layout(treedata)

    # create the form and show it without the plot
    window = sg.Window(WINDOW_TITLE, layout, finalize=True)

    # get problem-specific data tables
    # tables = get_tables()

    while True:
        event, values = window.read(timeout=50)
        if event == sg.WINDOW_CLOSED:
            break
        elif event == "import":
            employees = read_csv()
            new_treedata = build_treedata(employees)
            window["tree"].update(new_treedata)
    window.close()


if __name__ == "__main__":
    main()
