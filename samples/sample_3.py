import PySimpleGUI as sg
import numpy as np
from sqlalchemy import select
from matplotlib import ticker, rcParams
from matplotlib.pyplot import subplots
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


from actuarial.discounting import FixedInterest
from actuarial.db.session import session_fac
from actuarial.db.mappings.table import LifeTable
from actuarial.management.policy import Policy
from actuarial.products.annuity import TermLifeAnnuity
from actuarial.products.insurance import WLInsurance


# region Matplotlib Config


rcParams.update({"font.size": 6})

# endregion

# region GUI

WINDOW_TITLE = "PLACEHOLDER TITLE"


def draw_figure(canvas, figure, loc=(0, 0)):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side="top", fill="both", expand=1)
    return figure_canvas_agg


def get_config_frame():
    layout = [[sg.Text("hey")]]
    frame = sg.Frame("Config", layout, expand_y=True)
    return frame


def get_layout():
    layout = [[sg.Canvas(key="canvas"), get_config_frame()]]
    return layout


# endregion


def get_table() -> LifeTable:
    session = session_fac()

    stmt = select(LifeTable)
    table = session.execute(stmt).scalars().first()
    return table


def draw_benefits(ax, policy: Policy):
    death_bens, surv_bens = policy.benefit_curve()
    last_meaningful_yr = np.nonzero(policy.benefit_curve())[-1].max() + 1

    xvals = np.arange(last_meaningful_yr) + policy.age

    ax.stackplot(
        xvals,
        [death_bens[:last_meaningful_yr], surv_bens[:last_meaningful_yr]],
        labels=["Death", "Survival"],
    )
    ax.margins(0.06125, 0.125)
    ax.xaxis.set_major_locator(ticker.MultipleLocator(5))
    ax.legend()
    return


def draw_annuity(ax, policy: Policy):
    pmts_per_yr = np.trim_zeros(policy.payment_curve(), "b")
    xvals = np.arange(len(pmts_per_yr)) + policy.age

    ax.bar(xvals, pmts_per_yr, color="green")
    return


def main():
    # define the form layout
    sg.theme("Reddit")
    layout = get_layout()

    # create the form and show it without the plot
    window = sg.Window(WINDOW_TITLE, layout, finalize=True)
    canvas_elem = window["canvas"]
    canvas = canvas_elem.TKCanvas

    # draw the initial plot in the window
    fig, (ax1, ax2) = subplots(2, 1, figsize=(8, 6), constrained_layout=True)
    fig_agg = draw_figure(canvas, fig)

    # get problem-specific data tables
    table = get_table()

    i = FixedInterest(0.05)
    policy = Policy(30, [WLInsurance(table, i)], TermLifeAnnuity(10, table, i))

    while True:
        event, values = window.read(timeout=10)
        if event == sg.WINDOW_CLOSED:
            break

        for ax in (ax1, ax2):
            ax.set_axisbelow(True)
            ax.cla()  # clear the subplot
            ax.grid(axis="y")

        draw_benefits(ax1, policy)
        draw_annuity(ax2, policy)
        fig_agg.draw()
    window.close()


if __name__ == "__main__":
    main()
