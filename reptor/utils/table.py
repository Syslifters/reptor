from rich import box
from rich.table import Table

from typing import List, Optional


def make_table(columns: List[str], caption:  Optional[str] = None) -> Table:
    """This is a simpel helper function to ensure that all tables look the same
    Simply provide the columns you want to print out, as well as a specific caption.

    You can then use `table.add_row(finding.title, template.id)` to add the data
    according to your columns.

    In case you want to highlight a specific cell make use of the BBCode like
    syntax, such as [red]Important[/red]

    At the end call `reptor_console.print(table)` with your final table


    Args:
        columns (list[str]): Columns
        caption (str | None, optional): a Table caption at the bottom of the table. Defaults to None.

    Returns:
        Table: The raw table, without data, but with all styles set
    """

    table = Table(show_header=True, header_style="bold blue")
    if caption:
        table.caption = caption
    table.row_styles = ["none", "dim"]
    table.border_style = "bright_blue"
    table.box = box.SQUARE
    table.pad_edge = False

    for column in columns:
        table.add_column(column)

    return table
