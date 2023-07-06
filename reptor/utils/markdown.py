from rich.markdown import Markdown


def convert_markdown_to_console(markdown_in) -> Markdown:
    """Converts text markdown to rich.Console parsed markdown

    Args:
        markdown_in (str): raw markdown text

    Returns:
        Markdown: parsed Markdown from rich
    """
    return Markdown(markdown_in)
