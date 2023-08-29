# How to write a tool plugin
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

reptor uses the [Django template language](https://docs.djangoproject.com/en/4.2/ref/templates/language/){ target=_blank } with a slightly different syntax for formatting.  

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
This was automatically done in the `preprocess_for_template` method: 

```python
def preprocess_for_template(self):
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

## Uploading to notes

If you haven't done this so far, you can now add the configuration of your SysReptor installation.  
Create an API token at `https://yourinstallation.local/users/self/apitokens/` and run `reptor conf` to add all information.

Let's upload our formatted data to the project notes:

```bash
printf "https://example.com/alert(1)\nhttps://example.com/q=alert(1)" | reptor xsstool --upload
Successfully uploaded to notes.
```

If you experience any problems during upload, check if the user has permission for the project ID from your configuration. Use the `--debug` switch for further troubleshooting.

Your formatted output is now uploaded to your project notes:

![XssTool Note](/assets/xsstool-note.png)

Use `--notename "My Notename"` for a different title and `--personal-note` to not add it to a project, but to your personal notes instead.  

You can also update the default note title and replace your note icon in the `__init__` method:

```python
self.notename = kwargs.get("notename", "XSS Tool")
self.note_icon = "🔥"
```

### One note per target

What if we would like to have one note per target:

![XssTool Multiple Notes](/assets/xsstool-multinote.png)

Let's add the `--multi-notes` switch to the `add_arguments` method:

```python
parser.add_argument(
    "-multi-notes",
    "--multi-notes",
    help="Uploads multiple notes (one per target)",
    action="store_true",
)
```

(If your multiple notes should be the only option, omit the `add_argument` option and add `self.multi_notes = True` to your `__init__`.)

We now need to expand the `preprocess_for_template` method.  
It should still return a dictionary with the expected note titles as a key and a compatible data structure:

```json
{
  "https://example.com/alert(1)": {
    "data": [
      "https://example.com/alert(1)"
    ]
  },
  "https://example.com/q=alert(1)": {
    "data": [
      "https://example.com/q=alert(1)"
    ]
  }
}
```

We can do this by implementing:

```python
def preprocess_for_template(self):
    if not self.multi_notes:
        return super().preprocess_for_template()
    else:
        return {t: {"data": [t]} for t in self.parsed_input}
```

We can now upload one note per target as seen in the screenshot above:

```python
printf "https://example.com/alert(1)\nhttps://example.com/q=alert(1)" | reptor xsstool --upload --multi-notes                      
Successfully uploaded to notes.
```

## Create findings

Now we've reached the interesting part.  
Creating notes is nice but... We want to automate our report.

The first thing we need to define is a name for your finding and a condition when the finding should be triggered.

We call our finding `xss`. This means, we need to implement a method called `finding_xss`. This method should return data that can be used by Django templates. It many cases, the data might equal the return value of `preprocess_for_template`. The method should return `None` if no issue should be triggered.

In our case, we want to trigger an issue if the list in parsed input is not empty. Let's implement this method:

```python
def finding_xss(self):
    if len(self.parsed_input) > 0:
        return self.preprocess_for_template()
    return None
```

As soon as you have defined a `finding_*` method, you should have another option in your plugin's help message: `-push-findings, --push-findings`.

Now we have to define, what the contents of the findings should be. Find a sample finding in the `findings` directory.  
Rename this file to `xss.toml` to match it our vulnerability name.

The findings definitions are in [TOML](https://toml.io/){ target=_blank } format. Adapt the contents of the file, as needed, e. g.:

```toml
[data]
title = "Reflected Cross-Site Scripting (XSS)"
cvss = "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N"

summary = """
We detected a reflected XSS vulnerability.

<!--{% include "xss-list.md" %}-->
"""

recommendation = "HTML encode user-supplied inputs."
references = [
    "https://owasp.org/www-community/attacks/xss/",
]

```

You can use the adapted Django template language in the fields in the TOML structure.
Note that you can now include templates that we defined earlier as `xss-list.md`.  


We can use our new switch `--push-findings` and create a new finding in our SysReptor report:

```python
printf "https://example.com/alert(1)\nhttps://example.com/q=alert(1)" | reptor xsstool --push-findings
Pushed finding "Reflected Cross-Site Scripting (XSS)"
```

It was pushed to the SysReptor server and can be found in the project from the configuration:

![Pushed XSS finding](/assets/pushed-finding.png)

Note that no affected components were added to the finding. We can add the field `affected_components` as a list to the dictionary returned by our `finding_xss` method to be filled out:

```python
def finding_xss(self):
    if len(self.parsed_input) > 0:
        result = self.preprocess_for_template()
        result["affected_components"] = self.parsed_input
        return result
    return None
```

If you now push the finding again, it will not work because a finding with the same title already exists.  
Delete or rename the first finding, push again and the affected components will also be present in your finding.

## Create findings from SysReptor templates

We just created a finding from a TOML file.  
However, if you maintain your finding templates in SysReptor, you might want to create your findings from your centrally managed library.  

That's easier done than said: Add a tag to your finding template in the format `<plugin name>:<finding name>`. 
In our case this is `xsstool:xss`.

![Tag for finding template](/assets/template-tag.png)

We can use the string and markdown fields to insert our Django templates:

![Tag for finding template](/assets/django-template-in-finding-template.png)

The Django templates are now HTML comments. If you manually use your finding templates, the Django templates will not be rendered into your report. This is the reason the modified the Django tags.

Templates from the SysReptor template library are preferred over TOML-templates.

You can now generate your finding from your template library:

```bash
printf "https://example.com/alert(1)\nhttps://example.com/q=alert(1)" | reptor xsstool --push-findings
Pushed finding "Reflected Cross-Site Scripting (XSS)"
```

The finding was created successfully. You see from the "T" at the top that the finding was created from a template.

![Finding created from template library](/assets/finding-from-library.png)

If you now re-run the command, reptor will refuse to push the finding again. This is because the report holds a finding that was created from the same finding template.

