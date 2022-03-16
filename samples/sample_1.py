import PySimpleGUI as sg
from sqlalchemy import select
from matplotlib import ticker, rcParams
from matplotlib.pyplot import subplots
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from actuarial.discounting import FixedInterest
from actuarial.db.session import session_fac
from actuarial.db.mappings.table import LifeTable
from actuarial.products.insurance import WLInsurance, TermInsurance
from actuarial.products.annuity import WLAnnuity, TermLifeAnnuity

# Yet another usage of MatPlotLib with animations.
WINDOW_TITLE = "Visualization of Premiums vs Interest Rates and Terms"
TERMS = [5, 10, 15, 20, 25, 30, 35, 40]
WL_TERM = 80

rcParams.update({"font.size": 6})


def draw_figure(canvas, figure, loc=(0, 0)):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side="top", fill="both", expand=1)
    return figure_canvas_agg


def custom_slider(
    range_tup: tuple[int, int], def_val: float, key: str, resolution: float = 1
) -> sg.Slider:
    slider = sg.Slider(
        range=range_tup,
        default_value=def_val,
        size=(40, 10),
        orientation="h",
        key=key,
        enable_events=True,
        expand_x=True,
        resolution=resolution,
    )
    return slider


def get_layout():
    layout = [
        [sg.Canvas(key="canvas")],
        [sg.Text("Age")],
        [custom_slider((20, 60), 30, "age")],
        [sg.Text("Interest")],
        [custom_slider((0, 0.2), 0.05, "interest", 0.001)],
    ]
    return layout


def get_tables() -> list[LifeTable]:
    session = session_fac()

    stmt = select(LifeTable)
    tables = session.execute(stmt).scalars().all()
    return tables


def draw_insurance(ax, values, tables):
    int_rate = FixedInterest(values["interest"])
    age = int(values["age"])

    nsps = []
    for table in tables:
        prices = [TermInsurance(term, table, int_rate).epv(age) for term in TERMS]
        prices += [WLInsurance(table=table, i=int_rate).epv(age)]
        nsps.append((table.name, prices))

    xvals = [*TERMS, WL_TERM]
    for name, yvals in nsps:
        ax.plot(xvals, yvals, linewidth=1.0, marker="o", linestyle="--", label=name)
    ax.set(ylabel="EPV Insurance")
    ax.legend()
    return


def draw_annuity(ax, values, tables):
    int_rate = FixedInterest(values["interest"])
    age = int(values["age"])

    nsps = []
    for table in tables:
        prices = [TermLifeAnnuity(term, table, int_rate).epv(age) for term in TERMS]
        prices += [WLAnnuity(table=table, i=int_rate).epv(age)]
        nsps.append((table.name, prices))

    xvals = [*TERMS, WL_TERM]
    for name, yvals in nsps:
        ax.plot(xvals, yvals, linewidth=1.0, marker="o", linestyle="--", label=name)
    ax.set(ylabel="EPV Annuity")
    return


def draw_premium(ax, values, tables):
    int_rate = FixedInterest(values["interest"])
    age = int(values["age"])
    face_value = 500_000

    prems = []
    for table in tables:
        prices = [
            face_value
            * TermInsurance(term, table, int_rate).epv(age)
            / TermLifeAnnuity(term, table, int_rate).epv(age)
            for term in TERMS
        ]
        prices += [
            face_value
            * WLInsurance(table=table, i=int_rate).epv(age)
            / WLAnnuity(table=table, i=int_rate).epv(age)
        ]
        prems.append((table.name, prices))

    xvals = [*TERMS, WL_TERM]
    for name, yvals in prems:
        ax.plot(xvals, yvals, linewidth=1.0, marker="o", linestyle="--", label=name)
    ax.set(ylabel="Annual Premiums (Benefit: U$500,000)")
    return


@ticker.FuncFormatter
def label_formatter(x, pos):
    return x if x != WL_TERM else "WL"


def main():
    # define the form layout
    sg.theme("Reddit")
    layout = get_layout()

    # create the form and show it without the plot
    window = sg.Window(WINDOW_TITLE, layout, finalize=True)
    canvas_elem = window["canvas"]
    canvas = canvas_elem.TKCanvas

    # draw the initial plot in the window
    fig, (ax1, ax2, ax3) = subplots(
        3, 1, figsize=(8, 6), sharex=True, constrained_layout=True
    )
    fig_agg = draw_figure(canvas, fig)

    # get problem-specific data tables
    tables = get_tables()

    while True:
        event, values = window.read(timeout=10)
        if event == sg.WINDOW_CLOSED:
            break

        for ax in (ax1, ax2, ax3):
            ax.cla()  # clear the subplot
            ax.grid()  # draw the grid
            ax.xaxis.set_major_formatter(label_formatter)

        draw_insurance(ax1, values, tables)
        draw_annuity(ax2, values, tables)
        draw_premium(ax3, values, tables)

        fig_agg.draw()
    window.close()


if __name__ == "__main__":
    main()
