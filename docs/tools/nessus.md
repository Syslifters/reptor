## Examples

```bash title="Nessus"
cat nessus.xml | reptor nessus
cat nessus.xml | reptor nessus --upload  # Upload findings as notes
cat nessus.xml | reptor nessus --push-findings  # Create findings from scan results
cat nessus.xml | reptor nessus --include-plugins 11219,25216 --push-findings  # Include only plugin IDs 11219, 25216
cat nessus.xml | reptor nessus --exclude-plugins 11219,25216 --push-findings  # Exclude plugin IDs 11219, 25216
```

![Pushed Nessus findings](/cli/assets/nessus_uploaded_findings.png)

![Nessus findings as notes](/cli/assets/nessus_uploaded_notes.png)

## Usage
```
--8<-- "docs/cli/help-messages/nessus"
```
