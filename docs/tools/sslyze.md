## Examples

```bash title="SSLyze scan"
target=example.com:443
sslyze --sslv2 --sslv3 --tlsv1 --tlsv1_1 --tlsv1_2 --tlsv1_3 --certinfo --reneg --compression --heartbleed --openssl_ccs --fallback --robot "$target" --json_out=- | tee sslyze.json
```

```bash title="SSLyze"
cat sslyze.json | reptor sslyze  # Format
cat sslyze.json | reptor sslyze --upload  # Format and upload as note
cat sslyze.json | reptor sslyze --push-findings  # Create findings from scan results
reptor sslyze -i sslyze_1.json sslyze_2.json --push-findings  # Use multiple input files
```

![Pushed sslyze finding](/cli/assets/sslyze-finding.png)

## Usage
```
--8<-- "docs/cli/help-messages/sslyze"
```
