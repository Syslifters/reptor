<!--{% load md %}--><!--{% noemptylines %}-->
<!--{% if show_hostname %}-->

| Hostname | IP | Port | Service | Version |
| ------- | ------- | ------- | ------- | ------- |
<!--{% for service in data %}-->| <!--{{service.hostname}}--> | <!--{{service.ip}}--> | <!--{{service.port}}-->/<!--{{service.protocol}}--> | <!--{{service.service|default:"n/a"}}--> | <!--{{service.version|default:"n/a"}}--> |
<!--{% endfor %}-->

<!--{% else %}-->

| Host | Port | Service | Version |
| ------- | ------- | ------- | ------- |
<!--{% for service in data %}-->| <!--{{service.ip}}--> | <!--{{service.port}}-->/<!--{{service.protocol}}--> | <!--{{ service.service|default:"n/a"}}--> | <!--{{service.version|default:"n/a"}}--> |
<!--{% endfor %}-->
<!--{% endif %}-->

<!--{% endnoemptylines %}-->