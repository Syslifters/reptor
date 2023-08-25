# How to write a plugin
## What a plugin does

A plugin can...
* read tool outputs via stdin
* parse them
* format them
* upload as notes, or
* create findings

## Where plugins are located

reptor comes with a number of plugins.  
Howevers, you can override any plugin by copying it to the `.sysreptor/plugins` folder in your home directory.

You can do this by running `reptor plugins -copy <module name>`

If you copy the entire plugin, it fully overrides the plugins from reptor.  
You can also delete the python files from your home directory and leave the `templates` and `findings` directories. Then, you can customize the templates used for formatting the data, while preserving the official functionality of the plugin.

## Create a new plugin

Let's say we want to build a plugin for a fictional XSS-tool.  
We can start off using our plugin boilerplate by running `reptor plugins -new XssTool`.

This will add the file structure to `.sysreptor/plugins/XssTool`.  
This directory is already dynamically included by reptor. When you run `reptor --help`, you should see `xsstool` under the section `tool output processing`.  
You can also call the help message of your plugin by `reptor xsstool --help`.


## Implement a parser

Our XssTool has two output options:
* Plaintext
* JSON

Our plugin already implements some parsing methods and the corresponding arguments:
* `parse_json` (`--json`)
* `parse_xml` (`--xml`)
* `parse_csv` (`--csv`)

As we do not need xml and csv parsing, we can remove the methods. This will also make them disappear in the help message.  
The `parse_json` method will be called if the CLI switch `--json` is provided.  

However, we are missing an option to parse plaintext outputs.  
An example plaintext output would be:

```
https://example.com/alert(1)
https://example.com/q=alert(1)
```

Our parsing method should split the lines and store the result into a list:

```python
def parse_plaintext(self):
    self.parsed_input = self.raw_input.splitlines()
```

This function must also be called. We can override the parent's `parse` method for this.  
Calling the parent method makes sure that json parsing is executed.

```python
def parse(self):
    super().parse()
    if self.input_format == "plaintext":
        self.parse_plaintext()
```

We still need to add a commandline option for plaintext parsing. This can be done in the `add_arguments` method.  
In the course of this, let's delete the `--foo` and `--bar` commandline options of the boilerplate. We don't need them. (Make sure to leave the `super().add_arguments()` call.)

Input formats are mutually exclusive. We want our plaintext parsing switch also to be mutually exclusive. Therefore, we get the mutually exclusive parsing group and add a `--parse-plaintext` switch:

```python
@classmethod
def add_arguments(cls, parser, plugin_filepath=None):
    super().add_arguments(parser, plugin_filepath=plugin_filepath)
    input_format_group = cls.get_input_format_group(parser)
    input_format_group.add_argument(
        "-plaintext",
        "--plaintext",
        help="plaintext output format",
        action="store_const",
        dest="format",
        const="plaintext",
    )
```

The default `input_format` is `raw`. Specify the default `input_format` in the `__init__` method:

```python
if self.input_format == "raw":
    self.input_format = "plaintext"
```

We are now done with implementing our parser. We can test it using:

```bash
printf "https://example.com/alert(1)\nhttps://example.com/q=alert(1)" | reptor xsstool --parse      
['https://example.com/alert(1)', 'https://example.com/q=alert(1)']
```

## Formatting tool output

Now we want to bring our data into a beautiful and human-readable format. SysReptor uses markdown and allows HTML syntax there.

reptor uses the [Django template language](https://docs.djangoproject.com/en/4.2/ref/templates/language/) with a slightly different syntax for formatting.  

BLOCK_TAG_START = "<!--{%"
BLOCK_TAG_END = "%}-->"
VARIABLE_TAG_START = "<!--{{"
VARIABLE_TAG_END = "}}-->"
COMMENT_TAG_START = "<!--{#"
COMMENT_TAG_END = "#}-->"

The Django start tags are prepended with the HTML comment start tag and become:
* `{{` -> `<!--{{`
* `{%` -> `<!--{%`
* `{#` -> `<!--{#`

An HTML comment end tag is appended to the Django end tags:

* `}}` -> `}}-->`
* `%}` -> `%}-->`
* `#}` -> `#}-->`

(Find the reason for this later in this tutorial.)

Let's bring the list of our XSS outputs into the format of a markdown table.  
We find an empty template at `templates/default-template.md` in which we place the following template:

```md
| XSS target |
| ------- |
<!--{% for xss_target in data %}-->
| <!--{{xss_target}}--> |
<!--{% endfor %}-->
```

However, we have never defined the `data` variable.  
This was automatically done in the `process_parsed_input_for_template` method: 

```python
def process_parsed_input_for_template(self) -> typing.Optional[dict]:
    return {"data": self.parsed_input}
```

This method is like a second parsing step for preparing the parsed data for usage in a template. You can add entries to the dictionary for easier template processing.

We can now try to format our output:

```bash
printf "https://example.com/alert(1)\nhttps://example.com/q=alert(1)" | reptor xsstool --format 
| XSS target |
| ------- |

| https://example.com/alert(1) |

| https://example.com/q=alert(1) |
```

This gives us bad newlines within the table because the Django template engine leaves the newlines from the `for` loop there.  
However, in markdown newlines matter (contrarily to HTML).

We can resolve this by using the `noemptylines` tag (provided by reptor, not by Django):

```md
<!--{% load md %}--><!--{% noemptylines %}-->
| XSS target |
| ------- |
<!--{% for xss_target in data %}-->
| <!--{{xss_target}}--> |
<!--{% endfor %}-->
<!--{% endnoemptylines %}-->
```

You can now copy this template and add an additional template to get a markdown list instead of a table. Let's create `xss-list.md`:

```md
**XSS targets**

<!--{% load md %}--><!--{% noemptylines %}-->
<!--{% for xss_target in data %}-->
* <!--{{xss_target}}-->
<!--{% endfor %}-->
<!--{% endnoemptylines %}-->
```

Format your data using this template:

```bash
printf "https://example.com/alert(1)\nhttps://example.com/q=alert(1)" | reptor xsstool --format --template xss-list
**XSS target**

* https://example.com/alert(1)
* https://example.com/q=alert(1)
```

If you run `reptor xsstool --help` you see that the `--template` switch now takes two options:

```
-t {default-template,xss-list}
```

Those template names are taken from the filenames. The default template is the first in the list. Templates containing the word `default` are preferred.  
We can rename the file `default-template.md` to `default-xss-table.md` to have clearer options:

```
-t {default-xss-table,xss-list}
```

