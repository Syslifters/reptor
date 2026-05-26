# SSLyze

::: warning Deprecated
CLI importers are deprecated. Import scan results from the SysReptor web UI using the [scanimport](https://github.com/Syslifters/sysreptor/tree/main/plugins/scanimport) plugin instead.
:::

## Examples

```shell
target=example.com:443
sslyze --sslv2 --sslv3 --tlsv1 --tlsv1_1 --tlsv1_2 --tlsv1_3 --certinfo --reneg --compression --heartbleed --openssl_ccs --fallback --robot "$target" --json_out=- | tee sslyze.json
```

```shell
cat sslyze.json | reptor sslyze  # Format
cat sslyze.json | reptor sslyze --upload  # Format and upload as note
cat sslyze.json | reptor sslyze --push-findings  # Create findings from scan results
reptor sslyze -i sslyze_1.json sslyze_2.json --push-findings  # Use multiple input files
```

![Pushed sslyze finding](/cli/assets/sslyze-finding.png)

## Usage
<<< @/cli/help-messages/sslyze{txt}
