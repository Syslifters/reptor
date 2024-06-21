When using `reptor <plugin> --push-findings`, reptor aggregates all findings by scan plugin (so that, e.g., "SQL Injection" is only added once for multiple affected systems). It uses descriptions from the scanning tools.

But sometimes, you want to customize the finding descriptions or ratings. Here's how you do it.

*This description might not apply to all reptor tool plugins. It is, however, applicable at least to Nessus, OpenVAS, and Burp.*

Let's say we want to replace the title and the CVSS score of the SQL injection finding in a Burp report.

## Copy default templates to your home directory

The first step is to copy the templates shipped with reptor to your home directory. Use the following command:

```bash
reptor plugins --copy burp
```

This command copies the templates (usually in TOML format) to ~/.sysreptor/plugins/Burp/findings. Templates in this location override the default templates shipped with reptor. Changes in those templates are effective immediately. 

## Customize templates with static text
The `global.toml` template holds the information populated to SysReptor when pushing findings.

<figure markdown="span">
 ![Contents of global.toml](/cli/assets/burp_global_toml.png)
  <figcaption>Contents of global.toml</figcaption>
</figure>

The variables use the Django template language but with [different markers](/cli/writing-plugins/tools/#formatting-tool-output) (enclosed in HTML comments). Changes in this file will affect all findings pushed from the command line to your SysReptor report.

If we want to customize the Burp SQL injection finding, we first need to find out the plugin ID (Burp calls it "type") of the plugin. We find the ID 1049088 in the [Portswigger Knowledge Base](https://portswigger.net/kb/issues/00100200_sql-injection){ target=_blank } or in the notes if we upload Burp findings as notes (using `reptor burp -i burp.xml --upload`).

We now copy `global.toml` and name it `1049088.toml`. We can now change the title and the CVSS score to static values:

<figure markdown="span">
 ![Customized template](/cli/assets/burp_customized_sqli.png)
  <figcaption>Customized template</figcaption>
</figure>

If we now push the finding (e.g., using `reptor burp -i burp.xml --push-findings --include 1049088`), reptor uses our custom title.

## Customize templates with dynamic text
Burp includes lots of information in its reports that we do not use when pushing findings. You can check what variables exist using `reptor burp -i burp.xml --template-vars`.

You'll find, for example, the variable "confidence":

```
$ reptor burp -i burp.xml --template-vars
[
 {
 <snip>
 "severity": "high",
 "confidence": "Firm",
 <snip>
```

You can easily use this variable in your templates:

<figure markdown="span">
 ![Customized template with "confidence"](/cli/assets/burp_customized_sqli_1.png)
  <figcaption>Customized template with "confidence"</figcaption>
</figure>

## Populate your changes to your colleagues
Wouldn't it be nice if your colleagues could reuse your changes? That's easy.

Push your findings to your finding templates using `reptor burp --upload-finding-templates` (your user needs permission to edit finding templates).

<figure markdown="span">
 ![Pushed Burp SQLi template](/cli/assets/burp_pushed_finding_template.png)
  <figcaption>Pushed Burp SQLi template</figcaption>
</figure>

Finding templates having the tag "<plugin_name>:<plugin_id>" override local templates (shipped with reptor or in your home directory). The template is now effective for all SysReptor users using `reptor` to push Burp reports.
