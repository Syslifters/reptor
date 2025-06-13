## Examples

This importer supports both, Qualys *Web Application Scans* and *Vulnerability Management Scans*.  

*Limitations*: The Qualys XML exports don't include CVSS vectors, which is why CVSS scores are not populated to the findings. It, however, populates the "severity" field if your design uses it as a finding field.

```bash title="Qualys"
cat qualys.xml | reptor qualys
cat qualys.xml | reptor qualys --upload  # Upload findings as notes
cat qualys.xml | reptor qualys --push-findings  # Create findings from scan results
```

![Pushed Qualys findings](/cli/assets/qualys_uploaded_findings.png)

![Qualys findings as notes](/cli/assets/qualys_uploaded_notes.png)


Filter your Qualys results:

```bash title="Qualys Filter"
cat qualys.xml | reptor qualys --severity-filter medium-critical --push-findings
cat qualys.xml | reptor qualys --include-plugins 150158 --push-findings
cat qualys.xml | reptor qualys --exclude-plugins 150158 --push-findings
reptor qualys -i qualys_1.xml qualys_2.xml --push-findings  # Use multiple input files
```

You can add those filter settings to your config by running:

```bash title="OpenVAS conf"
reptor qualys --conf
```

## Usage
```
--8<-- "docs/cli/help-messages/qualys"
```
