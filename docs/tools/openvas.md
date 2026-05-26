# OpenVAS

::: warning Deprecated
CLI importers are deprecated. Import scan results from the SysReptor web UI using the [scanimport](https://github.com/Syslifters/sysreptor/tree/main/plugins/scanimport) plugin instead.
:::

## Examples

```shell
cat openvas.xml | reptor openvas
cat openvas.xml | reptor openvas --upload  # Upload findings as notes
cat openvas.xml | reptor openvas --push-findings  # Create findings from scan results
```

![Pushed OpenVAS findings](/cli/assets/openvas_uploaded_findings.png)

![OpenVAS findings as notes](/cli/assets/openvas_uploaded_notes.png)


Filter your OpenVAS results:

```shell
cat openvas.xml | reptor openvas --min-qod 50 --push-findings
cat openvas.xml | reptor openvas --severity-filter medium-critical --push-findings
cat openvas.xml | reptor openvas --include-plugins 1.3.6.1.4.1.25623.1.0.103674 --push-findings
cat openvas.xml | reptor openvas --exclude-plugins 1.3.6.1.4.1.25623.1.0.103674 --push-findings
reptor openvas -i openvas_1.xml openvas_2.xml --push-findings  # Use multiple input files
```

You can add those filter settings to your config by running:

```shell
reptor openvas --conf
```

## Usage
<<< @/cli/help-messages/openvas{txt}

## OpenVAS XML export

You can use the following filter to export all findings.
```
apply_overrides=0 min_qod=0 first=1 sort-reverse=severity rows=1000
```

If you want to export (more than 1.000) rows, set [`ignore_pagination="1"`](https://forum.greenbone.net/t/export-all-scan-results-from-a-single-report-or-multiple-when-then-are-more-than-1000-results/12383/8). 
One way to do this is to run the following commands as an **unprivileged user**.

```shell
user="your OpenVAS username"
report_id="your report id"
gvm-cli --gmp-username "$user" socket --xml "<get_reports report_id=\"$report_id\" ignore_pagination=\"1\" details=\"1\" />"
```
