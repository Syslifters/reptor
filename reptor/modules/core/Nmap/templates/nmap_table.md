{% load l10n %}
| Host | Port | Service | Version |
| ------- | ------- | ------- | ------- |
{% for service in data %}| {{service.ip}} | {{service.port|unlocalize}}/{{service.protocol}} | {{service.service|default:"n/a"}} | {{service.version|default:"n/a"}} |
{% endfor %}
