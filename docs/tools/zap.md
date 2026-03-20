## Examples
ZAP reports can be exported as XML or JSON.

```bash title="ZAP JSON"
cat zap.json | reptor zap
cat zap.json | reptor zap --upload  # Upload findings as notes
cat zap.json | reptor zap --push-findings  # Create findings from scan results
```

```bash title="ZAP XML"
cat zap.xml | reptor zap --xml
cat zap.xml | reptor zap --xml --upload  # Upload findings as notes
cat zap.xml | reptor zap --xml --push-findings  # Create findings from scan results
```

## Usage
```
--8<-- "docs/cli/help-messages/zap"
```
