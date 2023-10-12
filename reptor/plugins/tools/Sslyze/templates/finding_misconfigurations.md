<!--{% if has_misconfigurations %}-->
**Misconfigurations**

<!--{% load md %}--><!--{% oneliner %}-->
<!--{% if has_vulnerabilities or has_insecure_ciphers or has_insecure_protocols %}-->
Additionally, we
<!--{% else %}-->
We
<!--{% endif %}-->
detected the following misconfigurations:
<!--{% endoneliner %}-->

<!--{% noemptylines %}-->
|  | TLS Compression | Downgrade (no SCSV fallback) | No Secure Renegotiation | Client Renegotiation |
| ------- | ------- | ------- | ------- | ------- |
<!--{% for t in data %}-->
<!--{% oneliner %}-->
| <!--{{ t.hostname }}-->:<!--{{ t.port }}--> | 
<span style="color: <!--{{ t.misconfigurations.compression|yesno:"red,green" }}-->"><!--{{ t.misconfigurations.compression|yesno:"Yes,No" }}--></span> |
<span style="color: <!--{{ t.misconfigurations.downgrade|yesno:"red,green" }}-->"><!--{{ t.misconfigurations.downgrade|yesno:"Yes,No" }}--></span> |
<span style="color: <!--{{ t.misconfigurations.no_secure_renegotiation|yesno:"red,green" }}-->"><!--{{ t.misconfigurations.no_secure_renegotiation|yesno:"Yes,No" }}--></span> |
<span style="color: <!--{{ t.misconfigurations.accepts_client_renegotiation|yesno:"red,green" }}-->"><!--{{ t.misconfigurations.accepts_client_renegotiation|yesno:"Yes,No" }}--></span> |
<!--{% endoneliner %}-->
<!--{% endfor %}-->
<!--{% endnoemptylines %}--><!--{% endif %}-->