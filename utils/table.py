from rich import box
from rich.table import Table


def make_table(columns: list[str], caption: str | None = None):
    table = Table(show_header=True, header_style="bold yellow")
    if caption:
        table.caption = caption
    table.row_styles = ["none", "dim"]
    table.border_style = "bright_yellow"
    table.box = box.SQUARE
    table.pad_edge = False

    for column in columns:
        table.add_column(column)

    return table
