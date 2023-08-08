{% load l10n %}{% load md %}{% noemptylines %}
{% if data.show_hostname %}

| Hostname | Host | Port | Service | Version |
| ------- | ------- | ------- | ------- | ------- |
{% for service in data.parsed_input %}| {{service.hostname}} | {{service.ip}} | {{service.port|unlocalize}}/{{service.protocol}} | {{service.service|default:"n/a"}} | {{service.version|default:"n/a"}} |
{% endfor %}

{% else %}

| Host | Port | Service | Version |
| ------- | ------- | ------- | ------- |
{% for service in data.parsed_input %}| {{service.ip}} | {{service.port|unlocalize}}/{{service.protocol}} | {{service.service|default:"n/a"}} | {{service.version|default:"n/a"}} |
{% endfor %}
{% endif %}

{% endnoemptylines %}