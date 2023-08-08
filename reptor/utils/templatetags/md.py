from django import template

register = template.Library()

@register.tag
def noemptylines(parser, token):
    nodelist = parser.parse(("endnoemptylines",))
    parser.delete_first_token()
    return NoEmptyLinesNode(nodelist)


class NoEmptyLinesNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        output = self.nodelist.render(context)
        rendered = list()
        for line in output.splitlines():
            if line.strip():
                rendered.append(line)
        return "\n".join(rendered)