<!--{% load md %}--><!--{% noemptylines %}-->
 * Compression: <span style="color: <!--{% if misconfigurations.compression %}-->red<!--{% else %}-->green<!--{% endif %}-->"><!--{{ misconfigurations.compression|yesno:"Yes,No" }}--></span>
 * Downgrade Attack (no SCSV fallback): <span style="color: <!--{% if misconfigurations.downgrade %}-->red<!--{% else %}-->green<!--{% endif %}-->"><!--{{ misconfigurations.downgrade|yesno:"Yes,No" }}--></span>
 * No Secure Renegotiation: <span style="color: <!--{% if misconfigurations.no_secure_renegotiation %}-->red<!--{% else %}-->green<!--{% endif %}-->"><!--{{ misconfigurations.no_secure_renegotiation|yesno:"Yes,No" }}--></span>
 * Client Renegotiation: <span style="color: <!--{% if misconfigurations.accepts_client_renegotiation %}-->red<!--{% else %}-->green<!--{% endif %}-->"><!--{{ misconfigurations.accepts_client_renegotiation|yesno:"Yes,No" }}--></span>
<!--{% endnoemptylines %}-->
