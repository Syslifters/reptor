## Examples

```bash title="Burp"
cat burp.xml | reptor burp
cat burp.xml | reptor burp --upload  # Upload findings as notes
cat burp.xml | reptor burp --push-findings  # Create findings from scan results
```

<figure markdown="span">
  ![Pushed Burp findings](/cli/assets/burp_uploaded_findings.png)
  <figcaption>Pushed Burp findings</figcaption>
</figure>

<figure markdown="span">
  ![Burp findings as notes](/cli/assets/burp_uploaded_notes.png)
  <figcaption>Burp findings as notes</figcaption>
</figure>

Filter your Burp results:

```bash title="Burp Filter"
cat burp.xml | reptor burp --filter-severity medium-high --push-findings
cat burp.xml | reptor burp --include-plugins 2097928,2097936 --push-findings  # Include only plugin IDs 2097928, 2097936
cat burp.xml | reptor burp --exclude-plugins 2097928,2097936 --push-findings  # Exclude plugin IDs 2097928, 2097936
reptor burp -i burp_1.xml burp_2.xml --push-findings  # Use multiple input files
```

You can add those filter settings to your config by running:

```bash title="Burp conf"
reptor burp --conf
```

## Retrieve the XML file
Export the scanning results from [Burp Professional](https://portswigger.net/burp/documentation/desktop/getting-started/generate-reports){ target=_blank } or [Burp Enterprise](https://portswigger.net/burp/documentation/enterprise/user-guide/work-with-scan-results/generate-reports).  

## Known limitations
### All uploaded findings are rated as "Info"
Burp scans/reports don't offer a CVSS score. If you use CVSS scores for severity ratings in your SysReptor reports, all findings are rated as "Info" because the CVSS vector is not available.

<figure markdown="span">
  ![Burp findings rated as "Info"](/cli/assets/burp_findings_info.png)
  <figcaption>Burp findings rated as "Info"</figcaption>
</figure>

There are the following solutions:
1. Add CVSS ratings manually after the upload
2. [Add CVSS ratings to your finding templates](../customize-pushed-findings/)
3. Change the risk rating in your SysReptor design from CVSS to severity

## Usage
```
--8<-- "docs/cli/help-messages/burp"
```
