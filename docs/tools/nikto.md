## Examples

```bash title="Format nikto output"
cat nmap-output.xml | reptor nmap -oX
| Hostname | IP | Port | Service | Version |
| ------- | ------- | ------- | ------- | ------- |
| www.google.com | 142.250.180.228 | 80/tcp | http | gws |
| www.google.com | 142.250.180.228 | 443/tcp | https | gws |
| www.syslifters.com | 34.249.200.254 | 80/tcp | http | n/a |
| www.syslifters.com | 34.249.200.254 | 443/tcp | https | n/a |
```

```bash title="Upload table to notes"
cat nmap-output.xml | reptor nmap -oX --upload
```

## Usage
```
--8<-- "docs/cli/help-messages/nikto"
```
