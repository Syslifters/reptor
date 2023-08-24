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

We are now done with implementing our parser.

## Formatting tool output




