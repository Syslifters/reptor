# Configuration
```
reptor conf
Server [https://demo.sysre.pt]: 
API Token [Create at https://demo.sysre.pt/users/self/apitokens/]:
Project ID: 3fae023a-2632-4c88-a0ea-97ab5eb64c94
Store to config to C:\Users\user\.sysreptor\config.yaml? [y/n]:
```

Get your API token from https://{your-installation-url}/users/self/apitokens/.  
Find your project ID in the URL of your project (optional).

![Find the project ID in the URL](/cli/assets/project_id.png)

You can also add your configuration as environment variables. Environment variables override the config file.

```
export REPTOR_SERVER="https://demo.sysre.pt"
export REPTOR_TOKEN="sysreptor_ZDM5NmQ5<snip>"
export REPTOR_PROJECT_ID="3fae023a-2632-4c88-a0ea-97ab5eb64c94"
```

### Custom CA
If your SysReptor installation uses a self-signed certificate, you can specify the path to your CA bundle in your config file (`~/.sysreptor/config.yaml`):

```
requests_ca_bundle=/etc/ssl/certs/ca-certificates.crt
```

As an alternative, you can set it as environment variable:

```
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
```

Environment variables override config file settings.


### Usage
```
--8<-- "docs/cli/help-messages/reptor"
```
