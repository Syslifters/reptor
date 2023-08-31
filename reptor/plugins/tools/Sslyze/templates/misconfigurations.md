<!--{% load md %}--><!--{% noemptylines %}-->
 * Compression: <span style="color: <!--{% if target.misconfigurations.compression %}-->red<!--{% else %}-->green<!--{% endif %}-->"><!--{{ target.misconfigurations.compression|yesno:"Yes,No" }}--></span>
 * Downgrade Attack (no SCSV fallback): <span style="color: <!--{% if target.misconfigurations.downgrade %}-->red<!--{% else %}-->green<!--{% endif %}-->"><!--{{ target.misconfigurations.downgrade|yesno:"Yes,No" }}--></span>
 * No Secure Renegotiation: <span style="color: <!--{% if target.misconfigurations.no_secure_renegotiation %}-->red<!--{% else %}-->green<!--{% endif %}-->"><!--{{ target.misconfigurations.no_secure_renegotiation|yesno:"Yes,No" }}--></span>
 * Client Renegotiation: <span style="color: <!--{% if target.misconfigurations.accepts_client_renegotiation %}-->red<!--{% else %}-->green<!--{% endif %}-->"><!--{{ target.misconfigurations.accepts_client_renegotiation|yesno:"Yes,No" }}--></span>
<!--{% endnoemptylines %}-->
