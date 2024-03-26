## Examples

```bash title="Nessus"
cat nessus.xml | reptor nessus
cat nessus.xml | reptor nessus --upload  # Upload findings as notes
cat nessus.xml | reptor nessus --push-findings  # Create findings from scan results
```

![Pushed Nessus findings](/cli/assets/nessus_uploaded_findings.png)

![Nessus findings as notes](/cli/assets/nessus_uploaded_notes.png)

Filter your Nessus results:

```bash title="Nessus Filter"
cat nessus.xml | reptor nessus --filter-severity medium-critical --push-findings
cat nessus.xml | reptor nessus --include-plugins 11219,25216 --push-findings  # Include only plugin IDs 11219, 25216
cat nessus.xml | reptor nessus --exclude-plugins 11219,25216 --push-findings  # Exclude plugin IDs 11219, 25216
reptor nessus -i nessus_1.xml nessus_2.xml --push-findings  # Use multiple input files
```

You can add those filter settings to your config by running:

```bash title="Nessus conf"
reptor nessus --conf
```


## Usage
```
--8<-- "docs/cli/help-messages/nessus"
```
