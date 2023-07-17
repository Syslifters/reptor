{% load l10n %}
{% for target in data %}
# {{ target.hostname }}:{{ target.port|unlocalize }} ({{ target.ip_address }})
**Protocols**

{% if 'sslv2' in target.protocols %}
    * <span style="color: red">SSLv2</span>
{% endif %}
{% if 'sslv3' in target.protocols %}
    * <span style="color: red">SSLv3</span>
{% endif %}
{% if 'tlsv1' in target.protocols %}
    * <span style="color: red">TLS 1.0</span>
{% endif %}
{% if 'tlsv1_1' in target.protocols %}
    * <span style="color: red">TLS 1.1</span>
{% endif %}
{% if 'tlsv1_2' in target.protocols %}
    * <span style="color: red">TLS 1.2</span>
{% endif %}
{% if 'tlsv1_3' in target.protocols %}
    * <span style="color: red">TLS 1.3</span>
{% endif %}

**Certificate Information**

{% if target.certinfo.certificate_untrusted %}
    * <span style="color: red">Certificate untrusted by:</span>
{% else %}
    * <span style="color: green">Certificate is trusted</span>
{% endif %}

* Certificate matches hostname: 
<span style="color: {% if target.certinfo.certificate_matches_hostname %}green{% else %}red{% endif %}">
    {{ target.certinfo.certificate_matches_hostname|yesno:"Yes,No" }}
</span>

{% endfor %}
