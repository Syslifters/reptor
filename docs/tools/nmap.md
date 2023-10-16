## Examples

```bash title="Nmap scan"
sudo -n nmap -Pn -n -sV -oX - -p 0-65535 $target | tee nmap-output.xml
```

```bash title="Format nmap output"
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

![Uploaded nmap notes](/cli/assets/nmap-notes.png)


## Usage
```
--8<-- "docs/cli/help-messages/nmap"
```
