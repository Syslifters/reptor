<!--{% if has_insecure_ciphers or has_insecure_protocols %}-->
**Insecure Ciphers and Protocols**

<!--{% load md %}--><!--{% oneliner %}-->
We
<!--{% if has_vulnerabilities %}-->also<!--{% endif %}-->
found out that
<!--{{ affected_components_short|first }}-->
<!--{% if affected_components_short|length == 2 %}-->
and <!--{{ affected_components_short|last }}-->
<!--{% elif affected_components_short|length > 2 %}-->
and <!--{{ affected_components_short|length|add:"-1"|safe }}--> other services
<!--{% endif %}-->
had insecure ciphers or protocols enabled:
<!--{% endoneliner %}-->

<!--{% noemptylines %}-->
|  | SSLv2 | SSLv3 | TLS 1.0 | TLS 1.1 | Weak Ciphers | Insecure Ciphers |
| ------- | ------- | ------- | ------- | ------- | ------- | ------- |
<!--{% for t in data %}-->
<!--{% oneliner %}-->
| <!--{{ t.hostname }}-->:<!--{{ t.port }}--> | 
<span style="color: <!--{% if 'sslv2' in t.protocols %}-->red<!--{% else %}-->green<!--{% endif %}-->"><!--{% if 'sslv2' in t.protocols %}-->Yes<!--{% else %}-->No<!--{% endif %}--></span> |
<span style="color: <!--{% if 'sslv3' in t.protocols %}-->red<!--{% else %}-->green<!--{% endif %}-->"><!--{% if 'sslv3' in t.protocols %}-->Yes<!--{% else %}-->No<!--{% endif %}--></span> |
<span style="color: <!--{% if 'tlsv1' in t.protocols %}-->orange<!--{% else %}-->green<!--{% endif %}-->"><!--{% if 'tlsv1' in t.protocols %}-->Yes<!--{% else %}-->No<!--{% endif %}--></span> |
<span style="color: <!--{% if 'tlsv1_1' in t.protocols %}-->orange<!--{% else %}-->green<!--{% endif %}-->"><!--{% if 'tlsv1_1' in t.protocols %}-->Yes<!--{% else %}-->No<!--{% endif %}--></span> |
<span style="color: <!--{{ t.has_weak_ciphers|yesno:"orange,green" }}-->"><!--{{ t.has_weak_ciphers|yesno:"Yes,No" }}--></span> |
<span style="color: <!--{{ t.has_insecure_ciphers|yesno:"red,green" }}-->"><!--{{ t.has_insecure_ciphers|yesno:"Yes,No" }}--></span> |
<!--{% endoneliner %}-->
<!--{% endfor %}-->
<!--{% endnoemptylines %}--><!--{% endif %}-->