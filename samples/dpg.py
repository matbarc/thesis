import pyperclip as pc
import dearpygui.dearpygui as dpg

from actuarial.mortality.table import get_table_by_name, get_table_names, SULT
from actuarial.products.insurance import TermInsurance, WLInsurance
from actuarial.products.annuity import TermLifeAnnuity, WLAnnuity
from actuarial.mortality.import_csv import import_csv
from actuarial.db.session import Session
from actuarial.db.mappings.table import DBLifeTable
from actuarial.products.simple_getters import get_policy

# region cbs


def open_tab(name: str):
    tag = f"tab_{name}"
    TAB_INFO = {
        "tab_intro": ("Introduction", intro_layout),
        "tab_pr_calc": ("Probability Calculator", prob_calculator_layout),
        "tab_table_view": ("View Tables", view_tables_layout),
        "tab_ins_graphs": ("Product Visualization", ins_graph_layout),
        "tab_ins_calc": ("Insurance Calculator", ins_calc_layout),
        "tab_ins_special_calc": (
            "Special Insurance Calculator",
            ins_special_calc_layout,
        ),
    }

    info = TAB_INFO.get(tag)
    if not info:
        return
    else:
        label, layout_fcn = info

    if not unhide(tag):
        with dpg.tab(label=label, closable=True, parent="bar", tag=tag):
            layout_fcn()
    dpg.set_value("bar", tag)
    return


def unhide(tag):
    if dpg.does_alias_exist(tag):
        dpg.configure_item(tag, show=True)
        return True
    return False


def update_prob_result():
    table = get_table_by_name(dpg.get_value("pr_table"))

    is_death = dpg.get_value("pr_surv") == "D"
    age = parse_int(dpg.get_value("pr_age"))
    period = parse_int(dpg.get_value("pr_period"))
    deferral = parse_int(dpg.get_value("pr_deferral"))

    if is_death:
        prob = table.q_def(age=age, k=period, deferral=deferral)
    else:
        prob = table.p(age=age + deferral, k=period)

    change_result_text("pr_result", msg="The probability is ", result=prob)
    return


def update_ins_result():
    table = get_table_by_name(dpg.get_value("ins_calc_table"))
    product = dpg.get_value("ins_calc_prod")
    age = parse_int(dpg.get_value("ins_calc_age"))
    term = parse_int(dpg.get_value("ins_calc_term"))
    amount = parse_float(dpg.get_value("ins_calc_amt"))
    i = parse_float(dpg.get_value("ins_calc_int"))

    policy = get_policy(product, age, table, i, term, amount)
    change_result_text("ins_calc_epv", msg="The EPV is ", result=policy.epv())
    change_result_text("ins_calc_prem", msg="The annual premium is ", result="WIP")
    return


def update_table():
    new_life_table = get_table_by_name(dpg.get_value("view_table_combo"))
    dpg.delete_item("view_table", children_only=True)
    add_table_contents(new_life_table)
    return


def get_graph_series():
    TERMS = [5, 10, 15, 20, 25, 30]
    WL_TERM = 80

    interest = parse_float(dpg.get_value("graph_int"))
    age = parse_int(dpg.get_value("graph_age"))

    x_series = [*TERMS, WL_TERM]

    inss = [TermInsurance(age, term, SULT, interest).epv() for term in TERMS]
    inss += [WLInsurance(age, SULT, interest).epv()]

    anns = [TermLifeAnnuity(age, term, SULT, interest).epv() for term in TERMS]
    anns += [WLAnnuity(age, SULT, interest).epv()]

    prems = [50_000 * ins / ann for ins, ann in zip(inss, anns)]
    return x_series, inss, anns, prems


def redraw_series():
    x, ins, ann, prem = get_graph_series()

    dpg.set_value("scatter0", (x, ins))
    dpg.set_value("scatter1", (x, ann))
    dpg.set_value("scatter2", (x, prem))

    for i in range(3):
        dpg.fit_axis_data(f"y_axis{i}")
    return


def select_file(a, b, c):
    fname = b["file_name"]
    path = b["file_path_name"]

    dpg.set_value("import_fname", fname)
    dpg.configure_item("save_file_btn", user_data=(fname, path))
    dpg.configure_item("win_import", show=True)
    return


def import_name_handler():
    has_name = bool(dpg.get_value("import_name"))
    if has_name:
        dpg.configure_item("save_file_btn", enabled=True)
    else:
        dpg.configure_item("save_file_btn", enabled=False)
    return


def import_from_csv(name, path):
    if not name:
        msg = "Please select a name."

    else:
        try:
            rows = import_csv(path)
            with Session() as session:
                table = DBLifeTable(name)
                table.rows.extend(rows)
                session.add(table)
                # session.commit()

            msg = "Success!"

            dpg.configure_item("win_import", show=False)
        except Exception as e:
            print(e)
            msg = "Error in parsing file. Try again."

    with dpg.window(modal=True, tag="modal"):
        dpg.add_text(msg)
        dpg.add_button(
            label="Close", callback=lambda: dpg.configure_item("modal", show=False)
        )
    return


def parse_int(text: str) -> int:
    return int(text) if text else 0


def parse_float(text: str) -> int:
    return float(text) if text else 0


# endregion

# region Shortcuts


def add_nav_button(label: str, cb, indent: int = 0):
    return dpg.add_button(label=label, callback=cb, width=-1, indent=indent)


def add_table_combo(tag: str, cb=None):
    tables = get_table_names()
    dpg.add_combo(
        tables, label="Table", tag=tag, width=100, default_value="SULT", callback=cb
    )
    return


def add_table_contents(table):
    dpg.add_table_column(label="Age (x)", parent="view_table")
    dpg.add_table_column(label="Lives", parent="view_table")
    dpg.add_table_column(label="p_x", parent="view_table")
    dpg.add_table_column(label="q_x", parent="view_table")

    for age, lives in enumerate(table.lives):
        with dpg.table_row(parent="view_table"):
            dpg.add_text(age)
            dpg.add_text(f"{lives:.04f}")
            dpg.add_text(f"{table.p(age):.06f}")
            dpg.add_text(f"{table.q(age):.06f}")
    return


def add_clickable_result(tag: str):
    with dpg.group(horizontal=True):
        dpg.add_text(tag=f"{tag}_text")
        dpg.add_button(tag=tag, callback=lambda a, b, c: pc.copy(c))
        with dpg.tooltip(tag):
            dpg.add_text("Click to copy to clipboard.")
    return


def change_result_text(tag: str, msg: str, result: float):
    dpg.configure_item(f"{tag}_text", default_value=msg)
    dpg.configure_item(tag, label=result, user_data=result)
    return


# endregion

# region Tab Layouts


def intro_layout():
    dpg.add_text("WIP")
    return


def prob_calculator_layout():
    add_table_combo(tag="pr_table")
    dpg.add_combo(
        ["S", "D"], label="Survival/Death", tag="pr_surv", width=50, default_value="S"
    )
    dpg.add_input_int(label="Age", tag="pr_age", width=100)
    dpg.add_input_int(label="Period", tag="pr_period", width=100)
    dpg.add_input_int(label="Deferral", tag="pr_deferral", width=100, default_value=0)
    dpg.add_button(label="Calculate", callback=update_prob_result)
    dpg.add_spacer(height=20)

    add_clickable_result("pr_result")
    return


def ins_graph_layout():
    with dpg.group(horizontal=True):
        dpg.add_slider_float(
            label="Interest",
            tag="graph_int",
            default_value=0.05,
            max_value=0.2,
            min_value=0,
            no_input=True,
            width=200,
            callback=redraw_series,
        )
        dpg.add_slider_int(
            label="Age at issue",
            tag="graph_age",
            default_value=30,
            max_value=70,
            min_value=20,
            width=200,
            no_input=True,
            callback=redraw_series,
        )

    dpg.add_spacer(height=15)

    with dpg.subplots(3, 1, height=-1, width=-1):
        xvals, ins, ann, prem = get_graph_series()

        labels = ["Insurance", "Annuity", "Premium"]

        for i, y_series in enumerate([ins, ann, prem]):
            with dpg.plot(no_title=True, tag=f"plot{i}"):

                # REQUIRED create axis
                dpg.add_plot_axis(dpg.mvXAxis, tag=f"x_axis{i}", no_tick_labels=True)
                dpg.add_plot_axis(dpg.mvYAxis, label=labels[i], tag=f"y_axis{i}")
                dpg.add_scatter_series(
                    xvals,
                    y_series,
                    label="SULT",
                    tag=f"scatter{i}",
                    parent=f"y_axis{i}",
                )

        dpg.add_plot_legend(parent="plot1")
        dpg.configure_item("x_axis2", no_tick_labels=False, label="Term")
        dpg.set_axis_ticks(
            "x_axis2",
            tuple([(str(num), num) for num in xvals[:-1]] + [("WL", xvals[-1])]),
        )
    return


def import_prompt():
    with dpg.file_dialog(
        label="File", tag="import_file", callback=select_file, height=350
    ):
        dpg.add_file_extension("CSV(.csv){.csv}")

    with dpg.window(
        label="Import",
        tag="win_import",
        show=False,
        height=100,
        width=200,
        no_resize=True,
    ):
        dpg.add_input_text(
            label="Name", tag="import_name", callback=import_name_handler
        )
        dpg.add_input_text(label="File", tag="import_fname", readonly=True)
        dpg.add_button(
            label="Save",
            callback=lambda _, __, user_data: import_from_csv(*user_data),
            tag="save_file_btn",
            enabled=False,
        )
    return


def view_tables_layout():
    dpg.add_spacer(height=10)
    add_table_combo("view_table_combo", cb=update_table)
    dpg.add_spacer(height=20)

    table = get_table_by_name(dpg.get_value("view_table_combo"))

    with dpg.table(
        tag="view_table",
        row_background=True,
        borders_innerV=True,
        borders_outerV=True,
        delay_search=True,
    ):
        add_table_contents(table)
    return


def ins_calc_layout():
    products = ["WL", "Endowment", "PureEndowment", "Term"]

    with dpg.group(horizontal=True):
        dpg.add_combo(products, label="Product", tag="ins_calc_prod", width=212)
        add_table_combo("ins_calc_table")

    dpg.add_input_int(
        label="Age",
        tag="ins_calc_age",
        default_value=20,
        max_value=90,
        min_value=20,
        min_clamped=True,
        max_clamped=True,
    )
    dpg.add_input_int(
        label="Term",
        tag="ins_calc_term",
        min_value=0,
        min_clamped=True,
        max_clamped=True,
    )
    dpg.add_input_float(
        label="Interest",
        tag="ins_calc_int",
        default_value=0.05,
        max_value=0.2,
        min_value=0,
    )
    dpg.add_input_float(label="Amount", tag="ins_calc_amt", default_value=100_000)
    dpg.add_button(label="Calculate", callback=update_ins_result)
    dpg.add_spacer(height=20)

    add_clickable_result("ins_calc_epv")
    add_clickable_result("ins_calc_prem")
    return


def ins_special_calc_layout():
    return


# endregion

dpg.create_context()
dpg.create_viewport(title="Placeholder Title", width=800, height=600, y_pos=900)

with dpg.window(tag="Primary"):
    with dpg.group(horizontal=True):
        with dpg.group(width=200):
            with dpg.child_window(label="Nav", height=dpg.get_viewport_height() - 40):
                with dpg.collapsing_header(label="Mortality"):
                    with dpg.tree_node(label="Life Tables"):
                        add_nav_button(label="Import Tables", cb=import_prompt)
                        add_nav_button(
                            label="View Tables", cb=lambda: open_tab("table_view")
                        )
                    with dpg.tree_node(label="Probabilities"):
                        add_nav_button(
                            label="Open Calculator", cb=lambda: open_tab("pr_calc")
                        )

                with dpg.collapsing_header(label="Blocks of Business"):
                    add_nav_button(
                        label="Create Block",
                        cb=lambda: open_tab("block_create"),
                        indent=21,
                    )
                    add_nav_button(
                        label="View Blocks",
                        cb=lambda: open_tab("block_view"),
                        indent=21,
                    )

                with dpg.collapsing_header(label="Insurance"):
                    add_nav_button(
                        "Open Pricing Calculator",
                        cb=lambda: open_tab("ins_calc"),
                        indent=21,
                    )
                    add_nav_button(
                        "Open Special Insurance Calculator",
                        cb=lambda: open_tab("ins_special_calc"),
                        indent=21,
                    )
                    add_nav_button(
                        "Open Visualization",
                        cb=lambda: open_tab("ins_graphs"),
                        indent=21,
                    )

                with dpg.collapsing_header(label="Help"):
                    dpg.add_text("Try visiting the ")
                    dpg.add_button(
                        label="Introduction page",
                        small=True,
                        callback=lambda: open_tab("intro"),
                    )
                    dpg.add_text(
                        "If that doesn't work try contacting me at barce036@umn.edu.",
                        wrap=0,
                    )

            dpg.add_text("Matheus Barcellos - 2022", indent=15)

        with dpg.child_window(tag="win_tabs"):
            with dpg.tab_bar(tag="bar"):
                open_tab("intro")


dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("Primary", True)
dpg.start_dearpygui()
dpg.destroy_context()
